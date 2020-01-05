
function onLoaded() {
	var csInterface = new CSInterface();
	var appName = loadJSX();

	csInterface.evalScript('$._generic_ = {}');

	if (appName == "PPRO") {
		csInterface.evalScript('$._PPP_.keepPanelLoaded()');
		csInterface.evalScript('$._PPP_.registerProjectChangedFxn()');
		csInterface.evalScript('$._generic_.refreshAnimations = $._PPP_.refreshAnimations');
		csInterface.evalScript('$._generic_.updateWorkarea = $._PPP_.updateWorkarea');
		csInterface.evalScript('$._generic_.serializeAnimation = $._PPP_.persistTimelineToJSON');
		csInterface.evalScript('$._generic_.editAction = $._PPP_.editAction');
	}

	if (appName == "AEFT") {
		csInterface.evalScript('$._AE_.keepPanelLoaded()');
		csInterface.evalScript('$._generic_.refreshAnimations = $._AE_.refreshAnimations');
		csInterface.evalScript('$._generic_.updateWorkarea = $._AE_.updateWorkarea');
	}
}

/**
* Load JSX file into the scripting context of the product. All the jsx files in 
* folder [ExtensionRoot]/jsx & [ExtensionRoot]/jsx/[AppName] will be loaded.
*/
function loadJSX() {
	var csInterface = new CSInterface();

	// get the appName of the currently used app. For Premiere Pro it's "PPRO"
	var appName = csInterface.hostEnvironment.appName;
	var extensionPath = csInterface.getSystemPath(SystemPath.EXTENSION);

	// load general JSX script independent of appName
	var extensionRootGeneral = extensionPath + '/jsx/';
	csInterface.evalScript('$._ext.evalFiles("' + extensionRootGeneral + '")');

	// load JSX scripts based on appName
	var extensionRootApp = extensionPath + '/jsx/' + appName + '/';
	csInterface.evalScript('$._ext.evalFiles("' + extensionRootApp + '")');

	return appName;
}

function evalScript(script, callback) {
	new CSInterface().evalScript(script, callback);
}

function onClickButton(ppid) {
	var extScript = "$._ext_" + ppid + ".run()";
	evalScript(extScript);
}
