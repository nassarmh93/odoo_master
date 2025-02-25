import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { ControlPanel } from "@web/search/control_panel/control_panel";
import { multiFileUpload } from "@sign/backend_components/multi_file_upload";
import { SignStatusIndicator } from "@sign/backend_components/sign_status_indicator/sign_status_indicator";
import { SignTemplateCustomCogMenu } from "../cog_menu/sign_template_custom_cog_menu";
import { SignTemplateHeaderTags } from "./sign_template_header_tags";

export class SignTemplateControlPanel extends Component {
    static template = "sign.SignTemplateControlPanel";
    static components = {
        ControlPanel,
        SignStatusIndicator,
        SignTemplateCustomCogMenu,
        SignTemplateHeaderTags,
    };
    static props = {
        responsibleCount: { type: Number },
        isPDF: { type: Boolean },
        hasSignRequests: { type: Boolean },
        actionType: { type: String },
        signTemplate: { type: Object },
        goBackToKanban: { type: Function },
        signStatus: { type: Object },
        manageTemplateAccess: { type: Boolean },
        onTemplateSaveClick: { type: Function },
    };

    setup() {
        this.controlPanelDisplay = {};
        this.nextTemplate = multiFileUpload.getNext() ?? false;
        this.action = useService("action");
        this.orm = useService("orm");
    }

    get customCogMenuProps() {
        return {
            signTemplate: this.props.signTemplate,
            hasSignRequests: this.props.hasSignRequests,
            manageTemplateAccess: this.props.manageTemplateAccess,
            isPDF: this.props.isPDF,
            onTemplateSaveClick: this.props.onTemplateSaveClick,
        };
    }

    get templateHeaderTagsProps() {
        return {
            signTemplate: this.props.signTemplate,
            hasSignRequests: this.props.hasSignRequests,
        }
    }

    get showShareButton() {
        return this.props.actionType !== "sign_send_request" && this.props.responsibleCount <= 1;
    }

    async onSendClick() {
        await this.saveBeforeAction();
        this.action.doAction("sign.action_sign_send_request", {
            additionalContext: {
                active_id: this.props.signTemplate.id,
                sign_directly_without_mail: false,
                show_email: true,
            },
        });
    }

    async saveBeforeAction() {
        if (this.props.signStatus.isTemplateChanged) {
            await this.props.signStatus.save();
        }
    }

    async onSignNowClick() {
        await this.saveBeforeAction();
        this.action.doAction("sign.action_sign_send_request", {
            additionalContext: {
                active_id: this.props.signTemplate.id,
                sign_directly_without_mail: true,
            },
        });
    }

    async onShareClick() {
        await this.saveBeforeAction();
        const action = await this.orm.call("sign.template", "open_shared_sign_request", [
            this.props.signTemplate.id,
        ]);
        this.action.doAction(action);
    }

    async onNextDocumentClick() {
        await this.saveBeforeAction();
        const templateName = this.nextTemplate.name;
        const templateId = parseInt(this.nextTemplate.template);
        multiFileUpload.removeFile(templateId);
        this.action.doAction({
            type: "ir.actions.client",
            tag: "sign.Template",
            name: _t("Template %s", templateName),
            params: {
                sign_edit_call: "sign_template_edit",
                id: templateId,
                sign_directly_without_mail: false,
            },
        });
    }

}
