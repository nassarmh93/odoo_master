import { useState, useSubEnv } from "@odoo/owl";

import { ListController } from "@web/views/list/list_controller";

export class TimesheetTimerListController extends ListController {
    static template = "timesheet_grid.TimesheetTimerListController";

    setup() {
        super.setup();
        useSubEnv({
            config: {
                ...this.env.config,
                disableSearchBarAutofocus: true,
            },
        });
        this.timerState = useState({ reload: false });
    }

    get deleteConfirmationDialogProps() {
        this.timerState.reload = false;
        const dialogProps = super.deleteConfirmationDialogProps;
        if (this.model.root.selection.some((t) => t.data.is_timer_running)) {
            dialogProps.confirm = async () => {
                await this.model.root.deleteRecords();
                this.timerState.reload = true;
            }
        }
        return dialogProps;
    }
}
