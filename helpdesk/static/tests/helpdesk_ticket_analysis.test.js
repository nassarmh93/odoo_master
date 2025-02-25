import { describe, expect, test } from "@odoo/hoot";
import { animationFrame } from "@odoo/hoot-mock";

import { WebClient } from "@web/webclient/webclient";
import { clickOnDataset, setupChartJsForTests } from "@web/../tests/views/graph/graph_test_helpers";
import {
    contains,
    fields,
    getService,
    mockService,
    models,
    mountWithCleanup,
 } from "@web/../tests/web_test_helpers";

import { defineHelpdeskModels, helpdeskModels } from "./helpdesk_test_helpers";

describe.current.tags("desktop");

class HelpdeskTicketReportAnalysis extends models.Model {
    _name = "helpdesk.ticket.report.analysis";
    team_id = fields.Many2one({ relation: "helpdesk.team" });
    create_date = fields.Datetime();
    close_date = fields.Datetime();

    _records = [
        { id: 4, team_id: 1, create_date: "2024-12-04 00:00:00", close_date: "2024-12-15 00:00:00" },
        { id: 6, team_id: 1, create_date: "2024-12-04 00:00:00", close_date: "2024-12-16 00:00:00" },
        { id: 9, team_id: 2, create_date: "2024-12-04 00:00:00", close_date: "2024-22-16 00:00:00" },
    ];
    _views = {
        "graph,false": `
            <graph string="Tickets Analysis" sample="1" js_class="helpdesk_ticket_analysis_graph">
                <field name="team_id"/>
            </graph>
        `,
        "pivot,false": `
            <pivot string="Tickets Analysis" display_quantity="1" sample="1" js_class="helpdesk_ticket_analysis_pivot">
                <field name="team_id"/>
            </pivot>
        `,
        "cohort,false": `
            <cohort
                string="Tickets Analysis"
                date_start="create_date" date_stop="close_date" interval="week"
                sample="1" js_class="helpdesk_ticket_analysis_cohort"
            />
        `,
        "search,false": `<search/>`,
    };
}
helpdeskModels.HelpdeskTicketReportAnalysis = HelpdeskTicketReportAnalysis;
helpdeskModels.HelpdeskTicket._views = {
    "form,false": `<form><field name="name"/></form>`,
    "list,false": `<list><field name="name"/></list>`,
    "search,false": `<search><field name="name"/></search>`,
};
defineHelpdeskModels();
setupChartJsForTests();

async function mountView(viewName) {
    const view = await mountWithCleanup(WebClient);
    await getService("action").doAction({
        id: 1,
        name: "tasks analysis",
        res_model: "helpdesk.ticket.report.analysis",
        type: "ir.actions.act_window",
        views: [[false, viewName]],
    });
    return view;
}

test("helpdesk.ticket.report.analysis (graph): clicking on a bar leads to helpdesk.ticket list", async () => {
    mockService("action", {
        doAction({ res_model }) {
            expect.step(res_model);
            return super.doAction(...arguments);
        },
    });

    const view = await mountView("graph");
    await animationFrame();
    await clickOnDataset(view);
    await animationFrame();

    expect(".o_list_renderer").toBeDisplayed({ message: "Clicking on a bar should open a list view" });
    // The model of the list view that is opened consequently should be "helpdesk.ticket"
    expect.verifySteps([ "helpdesk.ticket.report.analysis", "helpdesk.ticket" ]);
});

test("helpdesk.ticket.report.analysis (pivot): clicking on a cell leads to helpdesk.ticket list", async () => {
    mockService("action", {
        doAction({ res_model }) {
            expect.step(res_model);
            return super.doAction(...arguments);
        },
    });

    await mountView("pivot");
    await animationFrame();
    await contains(".o_pivot_cell_value").click();
    await animationFrame();

    expect(".o_list_renderer").toBeDisplayed({ message: "Clicking on a cell should open a list view" });
    // The model of the list view that is opened consequently should be "helpdesk.ticket"
    expect.verifySteps([ "helpdesk.ticket.report.analysis", "helpdesk.ticket" ]);
});


test("helpdesk.ticket.report.analysis (cohort): clicking on a cell leads to helpdesk.ticket list", async () => {
    mockService("action", {
        doAction({ res_model }) {
            expect.step(res_model);
            return super.doAction(...arguments);
        },
    });

    await mountView("cohort");
    await animationFrame();
    await contains(".o_cohort_row_clickable td").click();
    await animationFrame();

    expect(".o_list_renderer").toBeDisplayed({ message: "Clicking on a row should open a list view" });
    // The model of the list view that is opened consequently should be "helpdesk.ticket"
    expect.verifySteps([ "helpdesk.ticket.report.analysis", "helpdesk.ticket" ]);
});
