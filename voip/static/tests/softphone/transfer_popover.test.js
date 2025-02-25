import { describe, test } from "@odoo/hoot";
import { advanceTime } from "@odoo/hoot-mock";
import {
    click,
    contains,
    insertText,
    start,
    startServer,
    triggerHotkey,
} from "@mail/../tests/mail_test_helpers";
import { setupVoipTests } from "@voip/../tests/voip_test_helpers";
import { serverState } from "@web/../tests/web_test_helpers";

describe.current.tags("desktop");
setupVoipTests();

test.tags("focus required");
test("TransferPopover input is pre-filled with external device number.", async () => {
    const externalDeviceNumber = "1337";
    const pyEnv = await startServer();
    pyEnv["res.users.settings"].create({
        external_device_number: externalDeviceNumber,
        user_id: serverState.userId,
    });
    await start();
    await click(".o_menu_systray button[title='Open Softphone']");
    // dropdown requires an extra delay before click (because handler is registered in useEffect)
    await contains("button[title='Open Numpad']");
    await click("button[title='Open Numpad']");
    // ensure initial focusing is done before inserting text to avoid focus reset
    await contains("input[placeholder='Enter the number…']:focus");
    await insertText("input[placeholder='Enter the number…']", "+380 (44) 4315351");
    await triggerHotkey("Enter");
    await advanceTime(5000);
    await click("button[title='Transfer']:enabled");
    await contains(".o-voip-TransferPopover input", { value: externalDeviceNumber });
});
