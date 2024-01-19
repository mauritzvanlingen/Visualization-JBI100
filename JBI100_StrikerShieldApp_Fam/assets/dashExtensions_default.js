window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, context) {
            const {
                min_rank,
                max_rank
            } = context.hideout;
            const rank = feature.properties.rank;
            if (rank >= min_rank && rank <= max_rank) {
                return {
                    fillColor: 'red',
                    color: 'grey',
                    weight: 0.5
                };
            }
            return {
                fillColor: 'grey',
                color: 'grey',
                weight: 0.5
            };
        },
        function1: function(feature, layer) {
            if (feature.properties && feature.properties.ADMIN) {
                layer.bindTooltip(feature.properties.ADMIN);
            }
        }
    }
});