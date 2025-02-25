import { Chrome } from "@point_of_sale/app/pos_app";
import { patch } from "@web/core/utils/patch";

patch(Chrome.prototype, {
    setup() {
        super.setup(...arguments);
        this.pos.data.connectWebSocket("DELIVERY_ORDER_COUNT", async (order_id) => {
            const response = await this.pos.data.call(
                "pos.config",
                "get_delivery_data",
                [this.pos.config.id],
                {}
            );
            this.pos.delivery_order_count = response.delivery_order_count;
            this.pos.delivery_providers = response.delivery_providers;
            this.pos.total_new_order = response.total_new_order;
            this.pos.delivery_providers_active = response.delivery_providers_active;
        });
    },
});
