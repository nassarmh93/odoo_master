import { makeKwArgs } from "@web/../tests/web_test_helpers";
import { registry } from "@web/core/registry";

function _mockGetGanttData({ kwargs, model }) {
    kwargs = makeKwArgs(kwargs);
    const { groups, length } = this.env[model].web_read_group({
        ...kwargs,
        aggregates: ["id:array_agg"],
    });

    const recordIds = [];
    for (const group of groups) {
        group.__record_ids = group["id:array_agg"]
        delete group["id:array_agg"]
        recordIds.push(...(group.__record_ids || []));
    }

    const { records } = this.env[model].web_search_read(
        [["id", "in", recordIds]],
        kwargs.read_specification,
        makeKwArgs({ context: kwargs.context })
    );

    const unavailabilities = {};
    for (const fieldName of kwargs.unavailability_fields || []) {
        unavailabilities[fieldName] = {};
    }

    const progress_bars = {};
    for (const fieldName of kwargs.progress_bar_fields || []) {
        progress_bars[fieldName] = {};
    }

    return { groups, length, records, unavailabilities, progress_bars };
}

registry.category("mock_rpc").add("get_gantt_data", _mockGetGanttData);
