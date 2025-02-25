import { Activity } from "@mail/core/common/activity_model";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

/** @type {import("models").Activity} */
const activityPatch = {
    requestSignature(onClose = () => {}, documentReference = false) {
        const additionalContext = {
            sign_directly_without_mail: false,
            default_activity_id: this.id,
        };
        if (documentReference) {
            additionalContext.default_reference_doc = documentReference;
        }
        return this.store.env.services.action.doAction(
            {
                name: _t("Signature Request"),
                type: "ir.actions.act_window",
                view_mode: "form",
                views: [[false, "form"]],
                target: "new",
                res_model: "sign.send.request",
            },
            { additionalContext, onClose }
        );
    },
};
patch(Activity.prototype, activityPatch);
