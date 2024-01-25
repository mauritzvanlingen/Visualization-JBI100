window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, context) {
            const country = feature.properties.ADMIN;
            const color_coun = context.hideout.countryToColor[country];
            return {
                fillColor: color_coun,
                color: 'None',
                weight: 0.5,
                fillOpacity: 1
            };
        },
        function1: function(feature, layer) {
            if (feature.properties && feature.properties.ADMIN) {
                layer.bindTooltip(feature.properties.ADMIN);
            }
        }
    }
});