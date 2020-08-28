$._PS_ = {
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
    refreshAnimations: function(root, prefix, fps) {
        // https://community.adobe.com/t5/photoshop/getting-the-path-of-linked-smart-object-ps-bug/td-p/8964254?page=1
        function processSmartObj(obj) {
            var localFilePath = "";
            var ref = new ActionReference();  
            ref.putIdentifier(charIDToTypeID('Lyr '), obj.id);
            var desc = executeActionGet(ref);
            var smObj = desc.getObjectValue(stringIDToTypeID('smartObject'));  
            try {
                var localFilePath = smObj.getPath(stringIDToTypeID('link'));
            }
            catch(e) {}
            return localFilePath;
        }
        // https://community.adobe.com/t5/photoshop/place-linked-using-script/m-p/10205986?page=3
        var doc = app.activeDocument;
        for (var i = 0; i < doc.layers.length; i++) {
            var currentLayer = app.activeDocument.layers[i];
            if (currentLayer.name.match(prefix)) {
                //alert(currentLayer.name)
                app.activeDocument.activeLayer = currentLayer;
                var currentFilePath = processSmartObj(currentLayer);
                //alert(currentFilePath);
                var idplacedLayerRelinkToFile = stringIDToTypeID("placedLayerRelinkToFile");
                var desc10 = new ActionDescriptor();
                var idnull = charIDToTypeID("null");
                desc10.putPath(idnull, new File(currentFilePath));
                executeAction(idplacedLayerRelinkToFile, desc10, DialogModes.NO);
            }
        }
        // if (!root) {
        //     root = app.project;
        // }
        // var numItems = root.items.length;
        // for (var i = 1; i <= numItems; i++) {
        //     var item = root.items[i];
        //     if (item.name.match(prefix) && item.name.match(/\.png$/)) {
        //         //http://docs.aenhancers.com/sources/filesource/#filesource
        //         item.mainSource.reload();
        //     }
        // }
	},
};