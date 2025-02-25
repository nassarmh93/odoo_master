import { MrpQualityCheckConfirmationDialog } from "./mrp_quality_check_confirmation_dialog";
import { formatFloat } from "@web/views/fields/formatters";

export class MrpRegisterProductionDialog extends MrpQualityCheckConfirmationDialog {
    static template = "mrp_workorder.MrpRegisterProductionDialog";
    static props = {
        ...MrpQualityCheckConfirmationDialog.props,
        qtyToProduce: { optional: true, type: Number },
        checkId: { optional: true, type: Number },
    };

    setup() {
        super.setup();
        const { product_qty, product_tracking } = this.recordData;
        if (this.props.qtyToProduce) {
            this.quantityToProduce = this.props.qtyToProduce;
        } else {
            this.quantityToProduce = product_tracking === "serial" ? 1 : product_qty;
        }
        this.formatFloat = formatFloat;
    }

    async doActionAndClose(action, saveModel = true, reloadChecks = false) {
        this.state.disabled = true;
        if (saveModel) {
            await this.props.record.save();
            // Calls `set_qty_producing` because the onchange won't be triggered.
            const args = [this.props.record.resIds];
            if (this.props.checkId) {
                args.push(this.props.checkId);
            }
            await this.props.record.model.orm.call("mrp.production", "set_qty_producing", args);
        }
        if (this.props.qualityCheckDone) {
            await this.props.qualityCheckDone();
        } else {
            await this.props.reload(this.props.record);
        }
        this.props.close();
    }

    async actionGenerateSerial() {
        await this.props.record.model.orm.call(
            this.props.record.resModel,
            "action_generate_serial",
            [this.props.record.resId]
        );
        await this.props.reload(this.props.record);
    }

    get lotInfo() {
        return {
            name: "lot_producing_id",
            record: this.props.record,
            context: {
                default_product_id: this.recordData.product_id[0],
                default_company_id: this.recordData.company_id[0],
            },
            domain: [
                "&",
                ["product_id", "=", this.recordData.product_id[0]],
                "|",
                ["company_id", "=", false],
                ["company_id", "=", this.recordData.company_id[0]],
            ],
        };
    }

    get qtyDoneInfo() {
        return {
            name: "qty_producing",
            record: this.props.record,
        };
    }
}
