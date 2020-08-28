$._AE_ = {
	keepPanelLoaded: function () {
		app.setExtensionPersistent("com.goodhertz.coldtype", 0);
	},
	getSep: function () {
		if (Folder.fs === 'Macintosh') {
			return '/';
		} else {
			return '\\';
		}
	},
	updateEventPanel: function (message) {
		app.setSDKEventMessage(message, 'info');
    },
    refreshAnimations: function(root, prefix, fps) {
        if (!root) {
            root = app.project;
        }
        var numItems = root.items.length;
        for (var i = 1; i <= numItems; i++) {
            var item = root.items[i];
            if (item.name.match(prefix) && item.name.match(/\.png$/)) {
                //http://docs.aenhancers.com/sources/filesource/#filesource
                item.mainSource.reload();
            }
        }
	},
};