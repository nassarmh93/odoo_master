import { Activity } from "@mail/core/common/activity_model";
import { Record } from "@mail/core/common/record";

import { patch } from "@web/core/utils/patch";

patch(Activity.prototype, {
    setup() {
        super.setup(...arguments);
        this.approver_id = Record.one("approval.approver");
    },
});
