import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { stepUtils } from "@web_tour/tour_service/tour_utils";
import { queryFirst } from "@odoo/hoot-dom";

import { markup } from "@odoo/owl";

export function dragAndDropSignItemAtHeight(from, height = 0.5, width = 0.5) {
    function triggerDragEvent(element, type, data = {}) {
        const event = new DragEvent(type, { bubbles: true });
        for (const key in data) {
            Object.defineProperty(event, key, {
                value: data[key],
            });
        }
        element.dispatchEvent(event);
    }

    const iframe = document.querySelector("iframe");
    const to = queryFirst(`:iframe .page[data-page-number="1"]`);
    const toPosition = to.getBoundingClientRect();
    toPosition.x += iframe.contentWindow.scrollX + to.clientWidth * width;
    toPosition.y += iframe.contentWindow.scrollY + to.clientHeight * height;

    const dataTransferObject = {};
    const dataTransferMock = {
        setData: (key, value) => {
            dataTransferObject[key] = value;
        },
        getData: (key) => dataTransferObject[key],
        setDragImage: () => {},
        items: [],
    };

    triggerDragEvent(from, "dragstart", {
        dataTransfer: dataTransferMock,
    });

    triggerDragEvent(to, "drop", {
        pageX: toPosition.x,
        pageY: toPosition.y,
        dataTransfer: dataTransferMock,
    });

    triggerDragEvent(from, "dragend");
}

registry.category("web_tour.tours").add("sign_tour", {
    url: "/odoo",
    steps: () => [
        stepUtils.showAppsMenuItem(),
        {
            trigger: '.o_app[data-menu-xmlid="sign.menu_document"]',
            content: markup(_t("Let's <b>prepare & sign</b> our first document.")),
            tooltipPosition: "bottom",
            run: "click",
        },
        {
            trigger: ".o_nocontent_help .o_sign_sample",
            content: _t("Try out this sample contract."),
            tooltipPosition: "bottom",
            run: "click",
        },
        {
            isActive: ["manual"],
            trigger: ".o_sign_field_type_button:contains(" + _t("Signature") + ")",
            content: markup(_t("<b>Drag & drop “Signature”</b> into the bottom of the document.")),
            tooltipPosition: "bottom",
            run: "drag_and_drop :iframe #viewer",
        },
        {
            isActive: ["auto"],
            trigger: ".o_sign_field_type_button:contains(" + _t("Signature") + ")",
            run() {
                dragAndDropSignItemAtHeight(this.anchor, 0.5, 0.25);
            },
        },
        {
            trigger: ".o_control_panel .o_sign_template_send",
            content: markup(
                _t(
                    "Well done, your document is ready!<br>Let's send it to get our first signature."
                )
            ),
            tooltipPosition: "bottom",
            run: "click",
        },
        {
            trigger: ".o_field_signer_x2many",
            content: markup(
                _t(
                    "Select the contact who should sign, according to their role.<br>In this example, select your own contact to sign the document yourself."
                )
            ),
            tooltipPosition: "bottom",
            run: "click",
        },
        {
            trigger: 'button[name="send_request"]',
            content: _t("Let's send the request by email."),
            tooltipPosition: "bottom",
            run: "click",
        },
        {
            trigger: ".o_control_panel .o_sign_sign_directly",
            content: markup(
                _t(
                    "Since you're the one signing this document, you can do it directly within Odoo.<br>External users can use the link provided by email."
                )
            ),
            tooltipPosition: "bottom",
            run: "click",
        },
        {
            trigger: ":iframe .o_sign_sign_item_navigator",
            content: _t("Follow the guide to sign the document."),
            tooltipPosition: "bottom",
            run: "click",
        },
        {
            trigger:
                ":iframe .o_sign_sign_item_navigator, :iframe .o_sign_sign_item[data-signature]",
            content: markup(
                _t(
                    "Draw your most beautiful signature!<br>You can also create one automatically or load a signature from your computer."
                )
            ),
            tooltipPosition: "bottom",
            run: "click",
        },
        {
            trigger: ":iframe body:not(:has(footer.modal-footer button.btn-primary))",
        },
        {
            trigger: ".o_sign_validate_banner button.o_validate_button",
            content: _t("Congrats, your signature is ready to be submitted!"),
            tooltipPosition: "top",
            run: "click",
        },
        {
            trigger: '.modal-dialog button:contains("' + _t("Close") + '")',
            content: markup(
                _t(
                    "That's it, all done!<br>The document is signed, and a copy has been sent by email to all participants, along with a traceability report."
                )
            ),
            tooltipPosition: "bottom",
            run: "click",
        },
    ],
});
