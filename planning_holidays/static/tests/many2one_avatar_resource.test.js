import { describe, expect, test } from "@odoo/hoot";
import { animationFrame } from "@odoo/hoot-mock";
import { contains, makeMockServer, mountView } from "@web/../tests/web_test_helpers";
import { definePlanningHolidaysModels } from "./planning_holidays_test_helpers";

describe.current.tags("desktop");
definePlanningHolidaysModels();

test("many2one_avatar_resource widget in list view with time-off idle", async () => {
    /* 1. Create data
           two type of records tested:
            - 2 planning slots linked to a human resource not linked to a user:
              the hr employee status should be displayed in avatar card popover
            - 2 planning slots linked to a human resource linked to a user:
              the im status of the user should be displayed in avatar card popover
    */

    const { env } = await makeMockServer();

    // partners
    const [lucindaPartnerId, cardenioPartnerID] = env["res.partner"].create([
        { name: "Lucinda" },
        { name: "Cardenio" },
    ]);

    // Users
    const [lucindaUserId, cardenioUserId] = env["res.users"].create([
        {
            name: "Lucinda",
            partner_id: lucindaPartnerId,
        },
        {
            name: "Cardenio",
            partner_id: cardenioPartnerID,
        },
    ]);

    // Resources
    const [resDoro, resFer, resluci, resCar] = env["resource.resource"].create([
        {
            name: "Dorothea",
            resource_type: "user",
            hr_icon_display: "presence_holiday_present",
            show_hr_icon_display: true,
        },
        {
            name: "Fernando",
            resource_type: "user",
            hr_icon_display: "presence_holiday_absent",
            show_hr_icon_display: true,
        },
        {
            name: "Lucinda",
            resource_type: "user",
            user_id: lucindaUserId,
            im_status: "leave_online",
        },
        {
            name: "Cardenio",
            resource_type: "user",
            user_id: cardenioUserId,
            im_status: "leave_away",
        },
    ]);

    // Employees
    const employeeDorotheaData = { name: "Dorothea" };
    const employeeFernandoData = { name: "Fernando" };
    const employeeLucindaData = {
        name: "Lucinda",
        user_id: lucindaUserId,
        user_partner_id: lucindaPartnerId,
    };
    const employeeCardenioData = {
        name: "Cardenio",
        user_id: cardenioUserId,
        user_partner_id: cardenioPartnerID,
    };
    env["hr.employee"].create([
        { ...employeeDorotheaData, resource_id: resDoro },
        { ...employeeFernandoData, resource_id: resFer },
        { ...employeeLucindaData, resource_id: resluci },
        { ...employeeCardenioData, resource_id: resCar },
    ]);
    // FIXME: Manually trigger recomputation of related fields
    env["resource.resource"]._applyComputesAndValidate();

    // Imitating the server behavior by creating an hr.employee.public record with the same data and same id
    env["hr.employee.public"].create([
        employeeDorotheaData,
        employeeFernandoData,
        employeeLucindaData,
        employeeCardenioData,
    ]);

    // Planning slots
    env["planning.slot"].create([
        {
            display_name: "Planning slot Dorothea",
            resource_id: resDoro,
            resource_type: "user",
            user_id: false,
        },
        {
            display_name: "Planning slot Fernando",
            resource_id: resFer,
            resource_type: "user",
            user_id: false,
        },
        {
            display_name: "Planning Slot Lucinda",
            resource_id: resluci,
            resource_type: "user",
            user_id: lucindaUserId,
        },
        {
            display_name: "Planning Slot Cardenio",
            resource_id: resCar,
            resource_type: "user",
            user_id: cardenioUserId,
        },
    ]);

    await mountView({
        type: "list",
        resModel: "planning.slot",
        arch: `
        <list>
            <field name="display_name"/>
            <field name="resource_id" widget="many2one_avatar_resource"/>
        </list>`,
    });

    // 1. Clicking on human resource's avatar with no user associated (status: presence_holiday_present)
    await contains(".o_m2o_avatar").click();
    await animationFrame();
    expect(".o_card_user_infos span").toHaveText("Dorothea");
    expect(".o_employee_presence_status .fa-plane.text-success").toHaveCount(1, {
        message: "The idle icon of a present employee on leave should be a green plane",
    });

    // 2. Clicking on human resource's avatar with no user associated (status: presence_holiday_absent)
    await contains(".o_m2o_avatar:eq(1)").click();
    await animationFrame();
    expect(".o_card_user_infos span").toHaveText("Fernando");
    expect(".o_employee_presence_status .fa-plane.text-warning").toHaveCount(1, {
        message: "The idle icon of an absent employee on leave should be an orange plane",
    });

    // 3. Clicking on human resource's avatar with a user associated (status: leave_online)
    await contains(".o_m2o_avatar:eq(2)").click();
    await animationFrame();
    expect(".o_card_user_infos span").toHaveText("Lucinda");
    expect(".o_user_im_status .fa-plane.text-success").toHaveCount(1, {
        message: "The idle icon of a connected user on leave should be a green plane",
    });

    // 4. Clicking on human resource's avatar with a user associated (status: leave_away)
    await contains(".o_m2o_avatar:eq(3)").click();
    await animationFrame();
    expect(".o_card_user_infos span").toHaveText("Cardenio");
    expect(".o_user_im_status .fa-plane.text-warning").toHaveCount(1, {
        message: "The idle icon of a afk user on leave should be an orange plane",
    });
});
