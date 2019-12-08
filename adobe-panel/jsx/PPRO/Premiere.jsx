$._PPP_={
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
	persistTimelineToJSON: function () {
		//return;
		
		var seq = app.project.activeSequence;
		if (seq) {
			var currentSeqSettings = app.project.activeSequence.getSettings();
			if (currentSeqSettings) {
				var ip = seq.getInPointAsTime();
				var op = seq.getOutPointAsTime();
				var fps = currentSeqSettings.videoFrameRate;
				var duration = seq.end;

				var projPath = new File(app.project.path);
				var parentDir = projPath.parent.parent;
				var outputName = app.project.activeSequence.name;
				var jsonExtension = '.json';
				var completeOutputPath = parentDir.fsName + $._PPP_.getSep() + outputName + jsonExtension;
				var outFile = new File(completeOutputPath);
				outFile.encoding = "UTF8";
				outFile.open("w", "TEXT", "????");

				var data = {};
				data.metadata = { "inPoint": ip.seconds, "outPoint": op.seconds, "duration": duration, "timebase": seq.timebase, "frameRate": fps.seconds };
				
				data.storyboard = [];

				var markers = seq.markers;
				if (markers) {
					var markerCount = markers.numMarkers;
					if (markerCount) {
						for (var thisMarker = markers.getFirstMarker(); thisMarker !== undefined; thisMarker = markers.getNextMarker(thisMarker)) {
							data.storyboard.push({
								name: thisMarker.name,
								start: thisMarker.start.seconds,
								end: thisMarker.end.seconds
							});
						}
					}
				}

				data.tracks = [];
				for (var ti = 0; ti < seq.videoTracks.numTracks; ti++) {
					var track = seq.videoTracks[ti];
					var trackData = {markers: [], clips: []};
					data.tracks.push(trackData);
					var firstClip = null;
					for (var ci = 0; ci < track.clips.numTracks; ci++) {
						var clip = track.clips[ci];
						trackData.clips.push({
							name: clip.name,
							start: clip.start.seconds,
							inPoint: clip.inPoint.seconds,
							end: clip.end.seconds,
							outPoint: clip.outPoint.seconds,
						});
						if (!firstClip) {
							firstClip = clip;
						}
					}
					if (firstClip) {
						var pi = firstClip.projectItem;
						var markers = pi.getMarkers();
						if (markers) {
							for (var marker = markers.getFirstMarker(); marker !== undefined; marker = markers.getNextMarker(marker)) {
								trackData.markers.push({
									name: marker.name,
									start: marker.start.seconds,
									end: marker.end.seconds
								});
							}
						}
					}
				}

				outFile.writeln(JSON.stringify(data));
				projPath.close();
				outFile.close();
			}
		}
	},
	refreshAnimations: function(root, prefix, fps) {
        //alert(app.project.rootItem.children);
        if (!root) {
            root = app.project.rootItem;
        }
        var updatedItems = [];
        var numItems = root.children.numItems;
		for (var i = 0; i < numItems; i++) {
			var currentItem = root.children[i];
			if (currentItem) {
                if (currentItem.name.match(prefix) && currentItem.name.match(/\.png$/)) {
                    //alert(currentItem.name);
                    currentItem.refreshMedia();
                    updatedItems.push(currentItem.name);
                    //pi.changeMediaPath(mp, false);
                }
                //currentItem.refreshMedia();
			}
        }
        //$._PPP_.updateEventPanel("refreshed >>> " + updatedItems.join("/"));
	},
	registerProjectChangedFxn: function () {
		var success	= app.bind("onProjectChanged", $._PPP_.persistTimelineToJSON);
	},
};
