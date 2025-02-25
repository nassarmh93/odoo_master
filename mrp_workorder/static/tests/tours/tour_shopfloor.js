import { registry } from "@web/core/registry";
import { assert } from "@stock/../tests/tours/tour_helper";
import { stepUtils } from "./tour_step_utils";

registry.category("web_tour.tours").add("test_shop_floor", {
    steps: () => [
        {
            content: "Select the workcenter the first time we enter in shopfloor",
            trigger: '.form-check:has(input[name="Jungle"])',
            run: "click",
        },
        {
            trigger: '.form-check:has(input[name="Jungle"]:checked)',
        },
        {
            trigger: "footer.modal-footer button.btn-primary",
            run: "click",
        },
        {
            trigger: '.o_control_panel_actions button:contains("Jungle")',
        },
        {
            content: "Open the employee panel",
            trigger: 'button[name="employeePanelButton"]',
            run: "click",
        },
        {
            content: "Add operator button",
            trigger: 'button:contains("Operator")',
            run: "click",
        },
        {
            content: "Scan Abbie Seedy's badge",
            trigger: ".modal-body .o_mrp_employee_tree_view",
            run: "scan 659898105101",
        },
        {
            trigger: ".o_mrp_employees_panel li.o_admin_user:contains(Abbie Seedy)",
        },
        {
            content: "Add operator button",
            trigger: "button:contains('Operator')",
            run: "click",
        },
        {
            content: "Select the Billy Demo employee",
            trigger: ".modal-body .o_mrp_employee_tree_view .o_data_row td:contains('Billy Demo')",
            run: "click",
        },
        {
            trigger: ".o_mrp_employees_panel li.o_admin_user:contains(Billy Demo)",
        },
        {
            content: "Go to workcenter Savannah from MO card",
            trigger: '.o_mrp_record_line button span:contains("Savannah")',
            run: "click",
        },
        {
            trigger: '.o_control_panel_actions button.active:contains("Savannah")',
        },
        {
            content: "Start the workorder on header click",
            trigger: '.o_finished_product span:contains("Giraffe")',
            run: "click",
        },
        {
            content: "Register production check",
            trigger: ".modal:not(.o_inactive_modal) .btn.fa-plus",
            run: "click",
        },
        {
            content: "Validate production check",
            trigger: '.modal:not(.o_inactive_modal) button:contains("Validate"):enabled',
            run: "click",
        },
        {
            trigger:
                '.modal:not(.o_inactive_modal):contains(Instructions) button[barcode_trigger="NEXT"]',
            run: "scan OBTNEXT",
        },
        {
            trigger: '.modal:not(.o_inactive_modal) .modal-title:contains("Register legs")',
        },
        {
            trigger: '.modal:not(.o_inactive_modal) span[data-tooltip="Quantity"]:contains("8.00")',
            run: "scan PRODUCT_LEG",
        },
        {
            trigger: '.modal:not(.o_inactive_modal) span[data-tooltip="Quantity"]:contains("9.00")',
            run: "scan PRODUCT_LEG",
        },
        {
            content: "Component not tracked registration and continue production",
            trigger:
                '.modal:not(.o_inactive_modal) span[data-tooltip="Quantity"]:contains("10.00")',
        },
        {
            content: 'Click on "Validate"',
            trigger: 'button[barcode_trigger="NEXT"]',
            run: "click",
        },
        {
            trigger: '.modal:not(.o_inactive_modal) .modal-title:contains("Register necks")',
        },
        {
            trigger: 'button[barcode_trigger="NEXT"]',
            run: "click",
        },
        {
            trigger: '.modal:not(.o_inactive_modal) .modal-title:contains("Release")',
        },
        {
            trigger: ".modal:not(.o_inactive_modal) .modal-header .btn-close",
            run: "click",
        },
        {
            content: "Open instruction",
            trigger: 'button:contains("Instructions")',
            run: "click",
        },
        {
            trigger: '.modal:not(.o_inactive_modal) .modal-title:contains("Release")',
        },
        {
            trigger: '.modal:not(.o_inactive_modal) button[barcode_trigger="NEXT"]',
            run: "click",
        },
        {
            content: "Close first operation",
            trigger: '.card-footer button[barcode_trigger="CLWO"]:contains(Mark as Done)',
            run: "click",
        },
        {
            trigger: '.o_control_panel_actions button:contains("Jungle")',
            run: "click",
        },
        {
            trigger: 'div.o_mrp_display_record:contains("Release") .card-header .fa-play',
            run: "click",
        },
        {
            content: "Open the WO setting menu again",
            trigger: '.o_mrp_display_record:contains("Release") .card-footer button.fa-gear',
            run: "click",
        },
        {
            content: "Add an operation button",
            trigger: '.modal:not(.o_inactive_modal) button[name="addComponent"]',
            run: "click",
        },
        {
            content: "Ensure the catalog is opened",
            trigger: ".modal:not(.o_inactive_modal) .o_product_kanban_catalog_view",
        },
        {
            content: "search Color",
            trigger: ".modal-body .o_searchview_input",
            run: "edit color",
        },
        {
            content: "Add Color",
            trigger: ".o_searchview_autocomplete .o-dropdown-item.focus",
            run: "press Enter",
        },
        {
            content: "Ensure the search is done",
            trigger: '.modal-body div.o_searchview_facet:contains("color")',
        },
        {
            trigger: '.modal-body:not(:has(article.o_kanban_record:not(:contains("Color"))))',
        },
        {
            content: "Add Color",
            trigger: '.modal article.o_kanban_record:contains("Color") button .fa-shopping-cart',
            run: "click",
        },
        {
            content: "Ensure the Color product is added",
            trigger: ".modal button .fa-trash",
        },
        {
            content: "Close the catalog",
            trigger: ".modal-header .btn-close",
            run: "click",
        },
        {
            trigger: "body:not(:has(.modal))",
        },
        {
            trigger: "div.o_mrp_display_record .card-header .fa-pause",
            run: "click",
        },
        {
            trigger: "div.o_mrp_display_record .card-header .fa-play",
        },
        {
            trigger: ".card-footer button[barcode_trigger=CLMO]",
            run: "click",
        },
        {
            trigger: ".o_nocontent_help",
        },
        {
            content: "Leave shopfloor",
            trigger: ".o_home_menu .fa-sign-out",
            run: "click",
        },
        {
            content: "Switch to Manufacturing",
            trigger: '.o_app[data-menu-xmlid="mrp.menu_mrp_root"]',
            run: "click",
        },
        {
            content: "Pick Production",
            trigger: '.o-dropdown[data-menu-xmlid="mrp.menu_mrp_manufacturing"]',
            run: "click",
        },
        {
            content: "Pick Manufacturing Orders",
            trigger: '.o-dropdown-item[data-menu-xmlid="mrp.menu_mrp_production_action"]',
            run: "click",
        },
        {
            content: "Create an MO",
            trigger: "button.o_list_button_add",
            run: "click",
        },
        {
            content: "Pick a product name",
            trigger: "input#product_id_0",
            run: "edit test_product",
        },
        {
            content: "Create the product",
            trigger: "a#product_id_0_0_0",
            run: "click",
        },
        {
            content: "Confirm MO creation",
            trigger: 'button[name="action_confirm"]',
            run: "click",
        },
        {
            content: "Switch back to Shop Floor",
            trigger: 'button[name="action_open_shop_floor"]',
            run: "click",
        },
        {
            content: "Validate the current workcenter and the default search filters",
            trigger: ".o_mrp_display_records",
            run: () => {
                // Get MO name from the breadcrumb.
                const mo = document.querySelector(".o_breadcrumb .o_back_button").textContent;
                // Get filters from the search bar as text.
                const filters = Array.from(document.querySelectorAll("small.o_facet_value")).map(
                    (elem) => elem.textContent
                );
                // The results must be the MO name, and the WO states for progress and ready, in this exact order.
                if (
                    filters.length !== 4 ||
                    filters[0] !== mo ||
                    filters[1] !== "MO Ready" ||
                    filters[2] !== "Ready" ||
                    filters[3] !== "In Progress"
                ) {
                    console.error(`Unexpected search filters: "${filters.join(", ")}"`);
                }
            },
        },
        {
            content: "Leave Shop Floor",
            trigger: ".o_home_menu .fa-sign-out",
            run: "click",
        },
        {
            trigger: ".o_apps",
        },
    ],
});

registry.category("web_tour.tours").add("test_shop_floor_auto_select_workcenter", {
    steps: () => [
        // Select 3 available Work Centers.
        { trigger: "input[name='Preparation Table 1']", run: "click" },
        { trigger: "input[name='Preparation Table 2']", run: "click" },
        { trigger: "input[name='Furnace']", run: "click" },
        { trigger: ".modal-footer button.btn-primary", run: "click" },
        {
            trigger: ".o_control_panel_actions button:nth-child(3)",
            run: () => {
                const selectionButtons = document.querySelectorAll(
                    ".o_control_panel_actions button.text-nowrap"
                );
                assert(selectionButtons.length, 3, "Three WC buttons should be visible");
            },
        },
        // Exit the Shop Floor and re-open it.
        { trigger: ".o_home_menu", run: "click" },
        { trigger: ".o_menuitem[href='/odoo/shop-floor']", run: "click" },
        { trigger: ".o_control_panel_actions button:first-child.active" },
        { trigger: ".o_control_panel_actions button:nth-child(2):not(.active)" },
        { trigger: ".o_control_panel_actions button:nth-child(3):not(.active)" },

        { trigger: ".o_control_panel_actions button.fa-plus", run: "click" },
        { trigger: ".o_mrp_workcenter_dialog" },
        { trigger: "input[name='All MO']", run: "click" },
        { trigger: "input[name='My WO']", run: "click" },
        { trigger: ".modal-footer button.btn-primary", run: "click" },

        // Exit/re-open the Shop Floor again then check first button is selected (not "All MO".)
        { trigger: ".o_home_menu", run: "click" },
        { trigger: ".o_menuitem[href='/odoo/shop-floor']", run: "click" },
        {
            trigger: ".o_action.o_mrp_display",
            run: () => {
                const selectedWC = document.querySelector(
                    ".o_control_panel_actions button:first-child.active"
                );
                assert(selectedWC.innerText.includes("Preparation Table 1"), true);
            },
        },
        // Unselect WCs then re-select them to change the order ("All MO" will be first.)
        { trigger: ".o_control_panel_actions button.fa-plus", run: "click" },
        { trigger: ".o_mrp_workcenter_dialog" },
        { trigger: "input[name='Preparation Table 1']", run: "click" },
        { trigger: "input[name='Preparation Table 2']", run: "click" },
        { trigger: "input[name='Furnace']", run: "click" },
        { trigger: ".modal-footer button.btn-primary", run: "click" },

        { trigger: ".o_web_client:not(.modal-open)" },
        { trigger: ".o_control_panel_actions button.fa-plus", run: "click" },
        { trigger: ".o_mrp_workcenter_dialog" },
        { trigger: "input[name='Preparation Table 1']", run: "click" },
        { trigger: "input[name='Preparation Table 2']", run: "click" },
        { trigger: "input[name='Furnace']", run: "click" },
        { trigger: ".modal-footer button.btn-primary", run: "click" },

        {
            trigger: ".o_web_client:not(.modal-open)",
            run: () => {
                const firstButton = document.querySelector(
                    ".o_control_panel_actions button:first-child"
                );
                assert(firstButton.innerText.includes("All MO"), true);
            },
        },

        // Exit/re-open the Shop Floor once again then check first button is "All MO" and is selected.
        { trigger: ".o_home_menu", run: "click" },
        { trigger: ".o_menuitem[href='/odoo/shop-floor']", run: "click" },
        {
            trigger: ".o_action.o_mrp_display",
            run: () => {
                const selectedWC = document.querySelector(
                    ".o_control_panel_actions button:first-child.active"
                );
                assert(selectedWC.innerText.includes("All MO"), true);
            },
        },
        // Check the MO is visible now but won't be once "Preparation Table 2" will be selected.
        { trigger: ".o_mrp_display_record .o_mrp_record_line:contains('Prepare the pizza')" },
        { trigger: ".o_control_panel_actions button.fa-plus", run: "click" },
        { trigger: ".o_mrp_workcenter_dialog" },
        { trigger: "input[name='All MO']", run: "click" },
        { trigger: "input[name='My WO']", run: "click" },
        { trigger: "input[name='Preparation Table 1']", run: "click" },
        { trigger: ".modal-footer button.btn-primary", run: "click" },
        // Exit/re-open the Shop Floor once again, "Preparation Table 2" should be the first WC.
        { trigger: ".o_home_menu", run: "click" },
        { trigger: ".o_menuitem[href='/odoo/shop-floor']", run: "click" },
        {
            trigger: ".o_view_nocontent .o_nocontent_help",
            run: () => {
                const selectedWC = document.querySelector(
                    ".o_control_panel_actions button:first-child.active"
                );
                assert(selectedWC.innerText.includes("Preparation Table 2"), true);
            },
        },
        // Exit the Shop Floor and open it from a WO form view.
        { trigger: ".o_home_menu", run: "click" },
        { trigger: ".o_menuitem[href='/odoo/work-centers']", run: "click" },
        { trigger: "button[data-menu-xmlid='mrp.menu_mrp_manufacturing']", run: "click" },
        { trigger: "a[data-menu-xmlid='mrp.menu_mrp_workorder_todo']", run: "click" },
        { trigger: "[name='workcenter_id'][data-tooltip='Furnace']", run: "click" },
        { trigger: "button[name='action_open_mes']", run: "click" },
        // Check whatever was selected, when we come from a WO form view, only its WC is displayed.
        {
            trigger: ".o_action.o_mrp_display",
            run: () => {
                const selectedWC = document.querySelector(
                    ".o_control_panel_actions button:first-child.active"
                );
                assert(selectedWC.innerText.includes("Furnace"), true);
                const selectionButtons = document.querySelectorAll(
                    ".o_control_panel_actions button.text-nowrap"
                );
                assert(selectionButtons.length, 1, "Only one WC buttons should be visible");
            },
        },
    ],
});

registry.category("web_tour.tours").add("test_shop_floor_my_wo_filter_with_pin_user", {
    steps: () => [
        // Select the right workcenter.
        { trigger: "input[name='My WO']", run: "click" },
        { trigger: "input[name='My WO']:checked" },
        { trigger: 'input[name="Winter\'s Workshop"]', run: "click" },
        { trigger: 'input[name="Winter\'s Workshop"]:checked' },
        { trigger: "footer.modal-footer button.btn-primary", run: "click" },
        // Open the employee panel and select first and second employees.
        { trigger: '.o_control_panel_actions button:contains("Winter\'s Workshop")' },
        { trigger: 'button[name="employeePanelButton"]', run: "click" },
        { trigger: "button:contains('Operator')", run: "click" },
        { trigger: ".modal-body td.o_data_cell:contains('John Snow')", run: "click" },
        { trigger: '.o_mrp_employees_panel .o_admin_user:contains("John Snow")' },
        { trigger: "button:contains('Operator')", run: "click" },
        { trigger: ".modal-body td.o_data_cell:contains('Queen Elsa')", run: "click" },
        // Enter the PIN code for second employee.
        ...stepUtils.enterPIN("41213"),
        { trigger: ".o_mrp_employees_panel .o_admin_user:contains('Queen Elsa')" },
        {
            content: "Display right Workcenter",
            trigger: '.o_control_panel_actions button:contains("Winter\'s Workshop")',
            run: "click",
        },
        { trigger: 'button:contains("Winter\'s Workshop").active' },
        {
            content: "Start the first WO with the second employee",
            trigger: ".o_mrp_display_record:first-child .card-title",
            run: "click",
        },
        { trigger: ".o_mrp_display_record.o_active" },
        { trigger: ".o_mrp_employees_panel li:contains(John Snow)", run: "click" },
        { trigger: ".o_admin_user:contains(John Snow)" },
        {
            content: "Start the second WO with the first employee",
            trigger: ".o_mrp_display_record:last-child .card-title",
            run: "click",
        },

        { trigger: ".o_mrp_display_record:contains('TEST/00002').o_active" },
        {
            content: 'Display "My WO" workorders',
            trigger: ".o_control_panel_actions button:contains('My WO')",
            run: "click",
        },
        // Check the right WO is displayed.
        {
            trigger: ".o_control_panel_actions button:contains(My WO).active",
            run: () => {
                const currentEmployeeEl = document.querySelector(".o_admin_user div.fw-bold");
                assert(currentEmployeeEl.innerText, "John Snow");
                const records = document.querySelectorAll(".o_mrp_display_record");
                assert(records.length, 1);
                const recordTitle = records[0].querySelector(".card-title>span").innerText;
                assert(recordTitle, "TEST/00002 - Build the Snowman");
            },
        },
        // Select the second employee and check only the right WO is shown.
        { trigger: ".o_mrp_employees_panel li:contains(Queen Elsa)", run: "click" },
        ...stepUtils.enterPIN("41213"),
        {
            trigger: ".o_admin_user:contains(Queen Elsa)",
            run: () => {
                const currentEmployeeEl = document.querySelector(".o_admin_user div.fw-bold");
                assert(currentEmployeeEl.innerText, "Queen Elsa");
                const records = document.querySelectorAll(".o_mrp_display_record");
                assert(records.length, 1);
                const recordTitle = records[0].querySelector(".card-title>span").innerText;
                assert(recordTitle, "TEST/00001 - Build the Snowman");
            },
        },
        // Select again the first employee and check again only its WO is displayed.
        { trigger: ".o_mrp_employees_panel li:contains(John Snow)", run: "click" },
        {
            trigger: ".o_admin_user:contains(John Snow)",
            run: () => {
                const currentEmployeeEl = document.querySelector(".o_admin_user div.fw-bold");
                assert(currentEmployeeEl.innerText, "John Snow");
                const records = document.querySelectorAll(".o_mrp_display_record");
                assert(records.length, 1);
                const recordTitle = records[0].querySelector(".card-title>span").innerText;
                assert(recordTitle, "TEST/00002 - Build the Snowman");
            },
        },
    ],
});

registry.category("web_tour.tours").add("test_generate_serials_in_shopfloor", {
    steps: () => [
        {
            content: "Make sure workcenter is available",
            trigger: '.form-check:has(input[name="Assembly Line"])',
            run: "click",
        },
        {
            trigger: '.form-check:has(input[name="Assembly Line"]:checked)',
        },
        {
            content: "Confirm workcenter",
            trigger: 'button:contains("Confirm")',
            run: "click",
        },
        {
            content: "Select workcenter",
            trigger: 'button.btn-light:contains("Assembly Line")',
            run: "click",
        },
        {
            content: "Open the wizard",
            trigger: '.o_mrp_record_line .text-truncate:contains("Register byprod")',
            run: "click",
        },
        {
            content: "Open the serials generation wizard",
            trigger: ".o_widget_generate_serials button",
            run: "click",
        },
        {
            content: "Input a serial",
            trigger: "#next_serial_0",
            run: "edit 00001",
        },
        {
            content: "Generate the serials",
            trigger: 'button.btn-primary:contains("Generate")',
            run: "click",
        },
        {
            content: "Save and close the wizard",
            trigger: '.o_form_button_save:contains("Save")',
            run: "click",
        },
        {
            content: "Set production as done",
            trigger: 'button.btn-primary:contains("Close Production")',
            run: "click",
        },
    ],
});

registry.category("web_tour.tours").add("test_canceled_wo", {
    steps: () => [
        {
            content: "Make sure workcenter is available",
            trigger: '.form-check:has(input[name="Assembly Line"])',
            run: "click",
        },
        {
            trigger: '.form-check:has(input[name="Assembly Line"]:checked)',
        },
        {
            content: "Confirm workcenter",
            trigger: 'button:contains("Confirm")',
            run: "click",
        },
        {
            content: "Check MO",
            trigger: 'button.btn-light:contains("Assembly Line")',
            run: () => {
                if (document.querySelectorAll("ul button:not(.btn-secondary)").length > 1) {
                    console.error("Multiple Workorders");
                }
            },
        },
    ],
});

registry.category("web_tour.tours").add("test_change_qty_produced", {
    steps: () => [
        {
            content: "Make sure workcenter is available",
            trigger: '.form-check:has(input[name="WorkCenter"])',
            run: "click",
        },
        {
            content: "Make sure that Workcenter was checked",
            trigger: '.form-check:has(input[name="WorkCenter"]:checked)',
        },
        {
            content: "Confirm workcenter",
            trigger: 'button:contains("Confirm")',
            run: "click",
        },
        {
            content: "Select workcenter",
            trigger: 'button.btn-light:contains("WorkCenter")',
            run: "click",
        },
        {
            content: "Open the wizard",
            trigger:
                '.o_mrp_record_line .text-decoration-line-through:contains("Register Production")',
            run: "click",
        },
        {
            content: "Edit the quantity producing",
            trigger: 'input[inputmode="decimal"]',
            run: "edit 3",
        },
        {
            content: "Validate",
            trigger: 'button.btn-primary:contains("Validate")',
            run: "click",
        },
        {
            content: "Waiting modal to close",
            trigger: "body:not(:has(.o_dialog))",
        },
        {
            content: "Mark the WorkOrder as Done",
            trigger: 'button.btn-primary:contains("Close Production")',
            run: "click",
        },
        {
            content: "Confirm consumption warning",
            trigger: 'button.btn-primary:contains("Confirm")',
            run: "click",
        },
        {
            content: "Dismiss backorder",
            trigger: 'button.btn-secondary:contains("No Backorder")',
            run: "click",
        },
        {
            content: "Check that there are no open work orders",
            trigger: ".o_nocontent_help",
        },
    ],
});

registry.category("web_tour.tours").add('test_mrp_manual_consumption_in_shopfloor', {
    steps: () => [
        {
            trigger: ".form-check:has(input[name='Nuclear Workcenter'])",
            run: "click"
        },
        {
            trigger: '.form-check:has(input[name="Nuclear Workcenter"]:checked)',
        },
        {
            trigger: "button:contains('Confirm')",
            run: "click"
        },
        {
            trigger: "button.btn-light:contains('Nuclear Workcenter')",
            run: "click"
        },
        {
            trigger: ".o_control_panel_actions button.active:contains('Nuclear Workcenter')",
        },
        {
            trigger: ".o_finished_product span:contains('Finish')",
            run: "click"
        },
        {
            trigger: ".o_mrp_display_record.o_active",
        },
        {
            trigger: ".o_mrp_record_line:not(.text-muted) span:contains('Component')",
        },
]});
