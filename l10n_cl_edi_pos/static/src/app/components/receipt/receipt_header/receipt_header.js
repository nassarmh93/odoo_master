import { ReceiptHeader } from "@point_of_sale/app/screens/receipt_screen/receipt/receipt_header/receipt_header";
import { patch } from "@web/core/utils/patch";

patch(ReceiptHeader.prototype, {
    get officeSelection() {
        return this.order.session._l10n_cl_sii_regional_office_selection[
            this.order.company_id.l10n_cl_sii_regional_office
        ];
    },
});
