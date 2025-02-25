import { Component, useState, onWillUnmount, useRef } from "@odoo/owl";
import { usePreparationDisplay } from "@pos_preparation_display/app/services/preparation_display_service";
import { Orderline } from "@pos_preparation_display/app/components/orderline/orderline";
import { computeFontColor } from "@pos_preparation_display/app/utils/utils";

const { DateTime } = luxon;

export class Order extends Component {
    static components = { Orderline };
    static template = "pos_preparation_display.Order";
    static props = {
        order: Object,
    };

    setup() {
        this.preparationDisplay = usePreparationDisplay();
        this.orderlinesContainer = useRef("orderlines-container");
        this.state = useState({
            duration: 0,
            productHighlighted: [],
        });

        this.actionInProgress = false;
        this._updateDuration();
        this.interval = setInterval(() => {
            this._updateDuration();
        }, 1000);

        onWillUnmount(() => {
            clearInterval(this.interval);
        });
    }

    _updateDuration() {
        this.state.duration = this._computeDuration();
    }

    get presetTime() {
        return DateTime.fromSQL(this.props.order.preset_time).toFormat("HH:mm");
    }

    get stage() {
        const order = this.props.order;
        return this.preparationDisplay.stages.get(order.stageId);
    }

    get fondColor() {
        return computeFontColor(this.stage.color);
    }

    getSortedOrderlines() {
        return this.props.order.orderlines.sort((a, b) => {
            const categoryA = this.preparationDisplay.getProductCategories(
                a.productCategoryIds
            )?.[0];
            const categoryB = this.preparationDisplay.getProductCategories(
                b.productCategoryIds
            )?.[0];
            if (!categoryA || !categoryB) {
                return 0;
            }
            if (categoryA.sequence === 0 && categoryB.sequence === 0) {
                return categoryA.id - categoryB.id;
            }
            return categoryA.sequence - categoryB.sequence;
        });
    }
    _computeDuration() {
        const timeDiff = this._getOrderDuration();

        if (timeDiff > this.stage.alertTimer) {
            this.isAlert = true;
        } else {
            this.isAlert = false;
        }

        return timeDiff;
    }

    _getOrderDuration() {
        return this.props.order.computeDuration();
    }

    async doneOrder() {
        if (this.props.order.stageId !== this.preparationDisplay.lastStage.id) {
            return;
        }

        this.props.order.displayed = false;
        this.preparationDisplay.doneOrders([this.props.order]);
    }

    get cardColor() {
        return "o_pdis_card_color_0";
    }

    async clickOrder() {
        if (this.actionInProgress) {
            return;
        }
        try {
            this.actionInProgress = true;
            const order = this.props.order;
            if (order.stageId === this.preparationDisplay.lastStage.id) {
                return;
            } else {
                await this.preparationDisplay.sendStrickedLineToNextStage(this.props.order);
            }
        } catch (error) {
            console.warn(error);
        } finally {
            this.actionInProgress = false;
        }
    }
}
