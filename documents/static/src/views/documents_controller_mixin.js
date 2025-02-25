import { useSearchBarToggler } from "@web/search/search_bar/search_bar_toggler";
import { _t } from "@web/core/l10n/translation";
import { omit } from "@web/core/utils/objects";
import { useSubEnv } from "@odoo/owl";

export const DocumentsControllerMixin = (component) =>
    class extends component {
        setup() {
            super.setup(...arguments);
            this.searchBarToggler = useSearchBarToggler();
            useSubEnv({
                searchBarToggler: this.searchBarToggler,
            });
        }

        get modelParams() {
            const modelParams = super.modelParams;
            modelParams.multiEdit = true;
            return modelParams;
        }

        /**
         * Return the common list of actions for the selected / previewed document folders.
         */
        getEmbeddedActions() {
            if (!this.model.targetRecords[0]?.data.available_embedded_actions_ids?.records.length) {
                return [];
            }
            const actionsList = this.model.targetRecords.map((d) =>
                d.data.available_embedded_actions_ids.records.map((rec) => ({
                    id: rec.resId,
                    name: rec.data.display_name,
                }))
            );
            const actionsListIds = actionsList.map((actions) => actions.map((a) => a.id));
            const _embeddedActions = actionsList[0].filter((action) =>
                actionsListIds.every((a) => a.includes(action.id))
            );
            return Object.fromEntries(_embeddedActions.map(e => [
                e.id,
                {
                    description: e.name,
                    callback: () => this.model.onDoAction(e.id),
                    groupNumber: 0
                }
            ]));
        }

        getTopBarActionMenuItems() {
            const selectionCount = this.targetRecords.length;
            const singleSelection = selectionCount === 1 && this.targetRecords[0];
            const embeddedActions = this.getEmbeddedActions();
            return {
                ...embeddedActions,
                download: {
                    isAvailable: () => singleSelection,
                    sequence: 50,
                    description: _t("Download"),
                    icon: "fa fa-download",
                    callback: () => this.model.onDownload(),
                    groupNumber: 1
                },
                share: {
                    isAvailable: () => singleSelection,
                    sequence: 51,
                    description: _t("Share"),
                    icon: "fa fa-share",
                    callback: () => this.model.onShare(),
                    groupNumber: 1
                },
            };
        }

        getStaticActionMenuItems() {
            const selectionCount = this.targetRecords.length;
            const userIsInternal = this.documentService.userIsInternal;
            const singleSelection = selectionCount === 1 && this.targetRecords[0];
            const isInTrash = this.env.searchModel.getSelectedFolderId() === 'TRASH';
            const editMode = this.targetRecords.every((r) => r.data.user_permission === 'edit');
            const someActive = this.targetRecords.some((r) => r.data.active);
            const someArchived = this.targetRecords.some((r) => !r.data.active);
            const menuItems = super.getStaticActionMenuItems();
            const topBarActions = this.env.isSmall ? this.getTopBarActionMenuItems() : {};
            return {
                ...omit(menuItems, "archive", "delete", "duplicate", "unarchive"),
                ...topBarActions,
                duplicate: {
                    isAvailable: () => this.model.canDuplicateRecords,
                    sequence: 50,
                    description: _t("Duplicate"),
                    icon: "fa fa-copy",
                    callback: () => this.model.onDuplicate(),
                    groupNumber: 1
                },
                trash: {
                    isAvailable: () => userIsInternal && editMode && someActive,
                    sequence: 55,
                    description: _t("Move to Trash"),
                    icon: "fa fa-trash",
                    callback: () => this.model.onArchive(),
                    groupNumber: 1
                },
                restore: {
                    isAvailable: () => someArchived,
                    sequence: 60,
                    description: _t("Restore"),
                    icon: "fa fa-history",
                    callback: () => this.model.onRestore(),
                    groupNumber: 1
                },
                delete: {
                    isAvailable: () => this.model.canDeleteRecords,
                    sequence: 65,
                    description: _t("Delete"),
                    icon: "fa fa-trash",
                    callback: () => this.model.onDelete(),
                    groupNumber: 1
                },
                rename: {
                    isAvailable: () => (userIsInternal || editMode) && singleSelection && !isInTrash,
                    sequence: 70,
                    description: _t("Rename"),
                    icon: "fa fa-edit",
                    callback: () => this.model.onRename(),
                    groupNumber: 2
                },
                details: {
                    isAvailable: () => singleSelection,
                    sequence: 75,
                    description: _t("Info & tags"),
                    icon: "fa fa-info-circle",
                    callback: () => this.model.onToggleChatter(),
                    groupNumber: 2
                },
                shortcut: {
                    isAvailable: () => userIsInternal && singleSelection && !isInTrash,
                    sequence: 80,
                    description: _t("Create Shortcut"),
                    icon: "fa fa-external-link-square",
                    callback: () => this.model.onCreateShortcut(),
                    groupNumber: 2
                },
                version: {
                    isAvailable: () => this.model.canManageVersions,
                    sequence: 85,
                    description: _t("Manage Versions"),
                    icon: "fa fa-history",
                    callback: () => this.model.onManageVersions(),
                    groupNumber: 2
                },
                lock: {
                    isAvailable: () => userIsInternal && singleSelection && !isInTrash,
                    sequence: 90,
                    description: singleSelection?.data?.lock_uid ? _t("Unlock") : _t("Lock"),
                    icon: "fa fa-lock",
                    callback: () => this.model.onToggleLock(),
                    groupNumber: 2
                },
                copy: {
                    isAvailable: () => selectionCount && !isInTrash,
                    sequence: 95,
                    description: _t("Copy Links"),
                    icon: "fa fa-link",
                    callback: () => this.model.onCopyLinks(),
                    groupNumber: 2
                },
                pdf: {
                    isAvailable: () => userIsInternal && selectionCount && this.targetRecords.every((record) => record.isPdf()) && !isInTrash,
                    sequence: 100,
                    description: singleSelection ? _t("Split PDF") : _t("Merge PDFs"),
                    icon: "fa fa-scissors",
                    callback: () => this.model.onSplitPDF(),
                    groupNumber: 2
                },
            };
        }
    };
