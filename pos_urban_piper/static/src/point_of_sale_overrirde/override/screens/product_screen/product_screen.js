import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";
import { BackButton } from "@point_of_sale/app/screens/product_screen/action_pad/back_button/back_button";

patch(ProductScreen, {
    components: {
        ...ProductScreen.components,
        BackButton,
    },
    back: _t("Back"),
});
