import { Document } from "./document_model";
import { DocumentsManageVersions } from "@documents/components/documents_manage_versions_panel/documents_manage_versions_panel";
import { EventBus, reactive } from "@odoo/owl";
import { browser } from "@web/core/browser/browser";
import { parseSearchQuery, router } from "@web/core/browser/router";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { user } from "@web/core/user";
import { debounce } from "@web/core/utils/timing";
import { session } from "@web/session";
import { formatFloat } from "@web/views/fields/formatters";
import { memoize } from "@web/core/utils/functions";

// Small hack, memoize uses the first argument as cache key, but we need the orm which will not be the same.
const loadMaxUploadSize = memoize((_null, orm) =>
    orm.call("documents.document", "get_document_max_upload_limit")
);

export class DocumentService {
    documentList;

    constructor(env, services) {
        this.env = env;
        /** @type {import("@mail/core/common/store_service").Store} */
        this.store = services["mail.store"];
        this.orm = services["orm"];
        this.action = services["action"];
        this.notification = services["notification"];
        this.dialog = services["dialog"];
        this.fileUpload = services["file_upload"];
        this.logAccess = debounce(this._logAccess, 1000, false);
        this.currentFolderAccessToken = null;
        this.bus = new EventBus();
        this.userIsDocumentManager = false;
        this.userIsDocumentUser = false;
        this.userIsErpManager = false;
        this.userIsInternal = false;
        // Init data
        const urlSearch = parseSearchQuery(browser.location.search);
        const { documents_init } = session;
        const openPreview =
            Boolean(urlSearch.documents_init_open_preview) || documents_init?.open_preview;
        const documentId =
            Number(urlSearch.documents_init_document_id) || documents_init?.document_id;
        this.documentIdToRestoreOnce = documentId;
        const initFolderId = urlSearch.documents_init_folder_id;
        const folderId = ["MY", "COMPANY", "SHARED", "TRASH"].includes(initFolderId)
            ? initFolderId
            : Number(initFolderId) || documents_init?.folder_id;
        this._initData = { documentId, folderId, openPreview };
        if (this._initData.folderId) {
            browser.localStorage.setItem("searchpanel_documents_document", this._initData.folderId);
        }
        this.getSelectionActions = null;
    }

    /**
     * @returns Document id to restore if there is one otherwise undefined.
     * Note: To ensure the document is restored only once, it returns always undefined after the first call.
     */
    getOnceDocumentIdToRestore() {
        const res = this.documentIdToRestoreOnce;
        this.documentIdToRestoreOnce = undefined;
        return res;
    }

    async start() {
        [
            this.userIsDocumentManager,
            this.userIsDocumentUser,
            this.userIsErpManager,
            this.userIsInternal,
        ] = await Promise.all([
            user.hasGroup("documents.group_documents_manager"),
            user.hasGroup("documents.group_documents_user"),
            user.hasGroup("base.group_erp_manager"),
            user.hasGroup("base.group_user"),
        ]);
        const initialState = this.userIsInternal && JSON.parse(localStorage.getItem("documentsChatterVisible"));
        this.chatterState = reactive({ visible: initialState }, () => {
            localStorage.setItem("documentsChatterVisible", this.chatterState.visible);
        });
    }

    /**
     * @param {Object} data
     * @returns {Document}
     */
    insert(data) {
        let document = this.store.Document.records[data.id];
        // Comparing the datapoint id here.
        if (document?.record.id !== data.record.id) {
            document = new Document();
            if ("id" in data) {
                document.id = data.id;
            }
            if ("attachment" in data) {
                document.attachment = this.store["ir.attachment"].insert(data.attachment);
            }
            if ("name" in data) {
                document.name = data.name;
            }
            if ("mimetype" in data) {
                document.mimetype = data.mimetype;
            }
            if ("url" in data) {
                document.url = data.url;
            }
            if ("displayName" in data) {
                document.displayName = data.displayName;
            }
            if ("record" in data) {
                document.record = data.record;
            }
            document.store = this.store;
            this.store.Document.records[data.id] = document;
            // Get reactive version.
            document = this.store.Document.records[data.id];
        }
        // return reactive version
        return document;
    }

    canUploadInFolder(folder) {
        return (
            folder &&
            ((typeof folder.id === "number" && folder.user_permission === "edit") ||
                (this.userIsInternal && ["MY", "RECENT", false].includes(folder.id)) ||
                (this.userIsDocumentManager && folder.id === "COMPANY"))
        );
    }

    canDownload(document) {
        return document && typeof document.id === "number";
    }

    isEditable(document) {
        return (
            document &&
            typeof document.id === "number" &&
            document.user_permission === "edit" &&
            (!document.is_company_root_folder || this.userIsDocumentManager)
        );
    }

    isFolderSharable(folder) {
        return folder && typeof folder.id === "number" && !folder.shortcut_document_id;
    }

    async openDialogDetails(documentId, editable) {
        return new Promise((resolve) => {
            this.action.doAction(
                {
                    type: "ir.actions.act_window",
                    res_model: "documents.document",
                    res_id: documentId,
                    views: [[false, "form"]],
                    target: "new",
                    context: {
                        active_id: documentId,
                        form_view_ref: "documents.document_view_form_details",
                        editable: Boolean(editable),
                        dialog_size: "medium",
                    },
                },
                {
                    onClose: async () => {
                        resolve();
                    },
                }
            );
        });
    }

    async openDialogRename(documentId) {
        return new Promise((resolve) => {
            this.action.doAction(
                {
                    name: _t("Rename"),
                    type: "ir.actions.act_window",
                    res_model: "documents.document",
                    res_id: documentId,
                    views: [[false, "form"]],
                    target: "new",
                    context: {
                        active_id: documentId,
                        dialog_size: "medium",
                        form_view_ref: "documents.document_view_form_rename",
                    },
                },
                {
                    onClose: async () => {
                        resolve();
                    },
                }
            );
        });
    }

    async openDialogManageVersions(documentId) {
        this.dialog.add(DocumentsManageVersions, { documentId });
    }

    async goToServerActionsView() {
        const userHasAccessRight = await user.checkAccessRight("ir.actions.server", "create");
        if (!userHasAccessRight) {
            return this.notification.add(
                _t("Contact your Administrator to get access if needed."),
                {
                    title: _t("Access to Server Actions"),
                    type: "info",
                }
            );
        }

        return await this.action.doActionButton({
            name: "action_open_documents_server_action_view",
            type: "object",
            resModel: "ir.actions.server",
        });
    }

    async createShortcut(documentIds) {
        if (documentIds.length !== 1) {
            this.notificationService.add(_t("Shortcuts can only be created one at a time."), {
                type: "danger",
            });
            return;
        }
        await this.orm.call("documents.document", "action_create_shortcut", documentIds);
    }

    async moveOrCreateShortcut(data, targetFolderId, forceShortcut) {
        let message = "";
        if (forceShortcut) {
            await this.orm.call("documents.document", "action_create_shortcut", [
                data.recordIds,
                targetFolderId,
            ]);
            message =
                data.recordIds.length == 1
                    ? _t("A shortcut has been created.")
                    : _t("%s shortcuts have been created.", data.recordIds.length);
        } else {
            if (data.movableRecordIds.length) {
                await this.orm.call("documents.document", "action_move_documents", [data.movableRecordIds, targetFolderId]);
                message =
                    data.movableRecordIds.length == 1
                        ? _t("The document has been moved.")
                        : _t("%s documents have been moved.", data.movableRecordIds.length);
            }
            if (data.nonMovableRecordIds.length) {
                await this.orm.call("documents.document", "action_create_shortcut", [data.nonMovableRecordIds, targetFolderId]);
                message = _t("At least one document couldn't be moved due to access rights. Shortcuts have been created.");
            }
        }
        this.notification.add(message, { type: "success" });
    }

    async toggleFavorite(document) {
        await this.orm.write("documents.document", [document.id], {
            is_favorited: !document.is_favorited,
        });
    }

    get initData() {
        return this._initData;
    }

    reload() {
        this.bus.trigger("DOCUMENT_RELOAD");
    }

    /**
     * Update the URL with the current folder/inspected document (as an access_token).
     *
     * Thanks to the provided arguments, this method adds the access_token of the currently
     * viewed document in the URL to allow the user to share the document (or the folder)
     * by simply sharing its URL.
     * When multiple document are viewed, it removes the access_token from the URL as sharing
     * multiple document with one URL is not supported.
     * Note that when the folderChange argument is undefined, the service use the preceding
     * given value if needed.
     *
     * @param folderChange the new folder or undefined if not changed
     * @param inspectedDocuments the currently inspected documents (can be undefined)
     */
    updateDocumentURL(folderChange, inspectedDocuments) {
        let accessToken;
        if (folderChange) {
            accessToken = folderChange.access_token;
            this.currentFolderAccessToken = accessToken;
        } else if (inspectedDocuments && inspectedDocuments.length === 1) {
            accessToken = inspectedDocuments[0].data.access_token;
        } else if (!inspectedDocuments || inspectedDocuments.length === 0) {
            accessToken = this.currentFolderAccessToken;
        } else {
            accessToken = undefined;
        }
        router.pushState({ access_token: accessToken });
    }

    /**
     * Refresh URL with the last folder (folderChange given to updateDocumentURL).
     *
     * Goal: When using an action the router loses its state.
     * This method is used to push the state already saved in this service
     * (the current folder) to the router state.
     */
    updateDocumentURLRefresh() {
        if (this.currentFolderAccessToken) {
            router.pushState({ access_token: this.currentFolderAccessToken });
        }
    }

    _logAccess(accessToken) {
        if (!accessToken) {
            return;
        }
        rpc(`/documents/touch/${accessToken}`);
    }

    /**
     * Return all the actions, and the embedded action for the given folders.
     *
     * EG: [{id: 1337, name: "Create Activity", is_embedded: true}, ...]
     */
    async getActions(folderId) {
        if (!this.userIsInternal) {
            return { actions: [] };
        }
        return await this.orm.call("documents.document", "get_documents_actions", [folderId]);
    }

    /**
     * Enable the action for the given folder.
     */
    async enableAction(folderId, actionId) {
        return await this.orm.call("documents.document", "action_folder_embed_action", [
            folderId,
            actionId,
        ]);
    }

    toggleChatterState() {
        this.chatterState.visible = !this.chatterState.visible;

        if (this.chatterState.visible) {
            this.observer = new MutationObserver(() => {
                const chatterContainer = document.querySelector('.o-mail-Thread');
                if (chatterContainer && this.env.isSmall) {
                    chatterContainer.scrollIntoView({ behavior: "smooth" });
                    this.observer.disconnect();
                    return;
                }
                const view = this.action.currentController.props.type;
                if (
                    chatterContainer &&
                    ["kanban", "list"].includes(view)
                ) {
                    const selectedRecordClass =
                        view === "kanban"
                            ? ".o_kanban_record.o_record_selected"
                            : ".o_data_row.o_data_row_selected";
                    const selectedRecords = document.querySelectorAll(selectedRecordClass);
                    if (selectedRecords?.length > 0) {
                        selectedRecords[0].scrollIntoView({
                            behavior: "instant",
                            block: view === "kanban" ? "start" : "center",
                        });
                    }
                    this.observer.disconnect();
                }
            });
            this.observer.observe(document.querySelector('.o_documents_content'), { childList: true, subtree: true });
        }
    }

    /**
     * Set the previewed document and send an event to notify the change.
     */
    setPreviewedDocument(document) {
        this.previewedDocument = document;
        this.bus.trigger("DOCUMENT_PREVIEWED");
    }

    async uploadDocument(files, accessToken, context) {
        const maxUploadSize = await loadMaxUploadSize(null, this.orm);
        const validFiles = [...files].filter((file) => file.size <= maxUploadSize);
        if (validFiles.length !== 0) {
            await this.fileUpload.upload(`/documents/upload/${accessToken || ""}`, validFiles, {
                buildFormData: (formData) => {
                    if (context) {
                        for (const key of [
                            "default_owner_id",
                            "default_partner_id",
                            "default_res_id",
                            "default_res_model",
                        ]) {
                            if (context[key]) {
                                formData.append(key.replace("default_", ""), context[key]);
                            }
                        }
                    }
                },
                displayErrorNotification: false,
            });
        }
        if (validFiles.length >= files.length) {
            return;
        }
        const message = _t(
            "Some files could not be uploaded (max size: %s).",
            formatFloat(maxUploadSize, { humanReadable: true })
        );
        this.notification.add(message, { type: "danger" });
    }
}

export const documentService = {
    dependencies: ["action", "mail.store", "notification", "orm", "dialog", "file_upload"],
    async start(env, services) {
        const service = new DocumentService(env, services);
        await service.start();
        return service;
    },
};

registry.category("services").add("document.document", documentService);
