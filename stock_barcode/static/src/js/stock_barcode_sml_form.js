import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { user } from "@web/core/user";
import { useService } from "@web/core/utils/hooks";
import { formView } from "@web/views/form/form_view";
import { FormController } from "@web/views/form/form_controller";
import { onWillStart } from "@odoo/owl";

export class StockBarcodeSmlFormController extends FormController {
    setup() {
        super.setup();
        this.dialogService = useService("dialog");
        this.orm = useService("orm");
        onWillStart(async () => {
            this.locationsEnabled = await user.hasGroup("stock.group_stock_multi_locations");
        });
    }

    /**
     * @override
     */
    async beforeExecuteActionButton(clickParams) {
        let proceed = true;
        if (clickParams.special && clickParams.special === "save") {
            const { data } = this.model.root;
            if (
                data.product_id &&
                this.locationsEnabled &&
                data.picking_code !== "incoming" &&
                data.qty_done > 0
            ) {
                const context = {
                    location: data.location_id[0],
                    lot_id: data.lot_id ? data.lot_id[0] : false,
                    package_id: data.package_id ? data.package_id[0] : false,
                    owner_id: data.owner_id ? data.owner_id[0] : false,
                    strict: true,
                };
                const [{ qty_available }] = await this.orm.searchRead(
                    "product.product",
                    [["id", "=", data.product_id[0]]],
                    ["qty_available"],
                    { context, limit: 1 }
                );
                if (!qty_available) {
                    proceed = await new Promise((resolve) => {
                        this.dialogService.add(ConfirmationDialog, {
                            body: _t(
                                "Oops! It seems that this product is not located in %(location)s.\nDo you confirm you picked from there?",
                                { location: data.location_id[1] }
                            ),
                            confirmLabel: _t("Confirm"),
                            confirm: () => resolve(true),
                            cancelLabel: _t("Discard"),
                            cancel: () => resolve(false),
                        });
                    });
                }
            }
        }
        return proceed && super.beforeExecuteActionButton(...arguments);
    }
}

export const stockBarcodeSmlFormView = {
    ...formView,
    Controller: StockBarcodeSmlFormController,
};

registry.category("views").add("stock_barcode_sml_form", stockBarcodeSmlFormView);
