var tl;
function onLoad() {
    var tl_el = document.getElementById("tl");
    var eventSource1 = new Timeline.DefaultEventSource();
    
    var theme1 = Timeline.ClassicTheme.create();
    //theme1.autoWidth = true; // Set the Timeline's "width" automatically.
			     // Set autoWidth on the Timeline's first band's theme,
			     // will affect all bands.
    theme1.timeline_start = new Date(Date.UTC(2012, 12, 1));
    theme1.timeline_stop  = new Date(Date.UTC(2013, 1, 1));
    
    var d = "Wed Jan 03 2013 13:00:00 GMT+0100"
    var bandInfos = [
	Timeline.createBandInfo({
	    width:          "300", // set to a minimum, autoWidth will then adjust
	    intervalUnit:   Timeline.DateTime.DAY,
	    intervalPixels: 1200,
	    eventSource:    eventSource1,
	    date:           d,
	    theme:          theme1,
	    layout:         'original'  // original, overview, detailed
	}),
	Timeline.createBandInfo({
	    width:          "30", 
	    intervalUnit:   Timeline.DateTime.DAY, 
	    intervalPixels: 200,
	    eventSource:    eventSource1,
	    date:           d, 
	    overview:       true
	   // theme:          theme
	})
    ];
    bandInfos[1].syncWith = 0;
    bandInfos[1].highlight = true;

    // Asynchronous Callback functions. Called after data arrives.
    function load_json1(json, url) {
      // Called with first json file from server
      // Also initiates loading of second Band
      eventSource1.loadJSON(json, url);
      // stop browser caching of data during testing by appending time
      //tl.loadJSON("cubism1.js?"+ (new Date().getTime()), load_json2);
	tl.finishedEventLoading();
    };
						    
    // create the Timeline
    tl = Timeline.create(tl_el, bandInfos, Timeline.HORIZONTAL);
    tl.loadJSON("/calls/all?"+ (new Date().getTime()), load_json1);

}

var resizeTimerID = null;
function onResize() {
    if (resizeTimerID == null) {
	resizeTimerID = window.setTimeout(function() {
	    resizeTimerID = null;
	    tl.layout();
	}, 500);
    }
}

