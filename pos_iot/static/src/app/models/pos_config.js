import { PosConfig } from "@point_of_sale/app/models/pos_config";
import { patch } from "@web/core/utils/patch";

patch(PosConfig.prototype, {
    get useProxy() {
        return super.useProxy || (this.iot_device_ids && this.iot_device_ids.length > 0);
    },
});
