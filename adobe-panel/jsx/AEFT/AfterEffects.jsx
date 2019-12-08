//#include "Premiere_JSON.jsx"

$._AE_ = {
	keepPanelLoaded: function () {
		app.setExtensionPersistent("com.goodhertz.coldtype", 0); // 0, while testing (to enable rapid reload); 1 for "Never unload me, even when not visible."
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
		//app.setSDKEventMessage('Here is some information.', 'info');
		//app.setSDKEventMessage('Here is a warning.', 'warning');
		//app.setSDKEventMessage('Here is an error.', 'error');  // Very annoying; use sparingly.
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