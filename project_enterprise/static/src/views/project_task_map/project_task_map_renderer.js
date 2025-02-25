import { onWillStart } from "@odoo/owl";

import { MapRenderer } from "@web_map/map_view/map_renderer";
import { user } from "@web/core/user";

export class ProjectTaskMapRenderer extends MapRenderer {
    static template = "project_enterprise.ProjectTaskMapRenderer";

    setup() {
        super.setup()
        onWillStart(async () => {
            this.isProjectManager = await user.hasGroup('project.group_project_manager');
        });
    }
}
