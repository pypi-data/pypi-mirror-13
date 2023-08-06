// $Id: scorm_apiwrapper.js e305c7a0c8d6 2015/07/30 14:27:09 Patrick $

/*jshint globalstrict: true*/
/*global jQuery: true */


// local variable definitions
var debug = false;
var lmsInitCalled = false;
var lmsFinishCalled = false;
var apiHandle = null;

// Define exception/error codes
var ERR_NO_ERROR = 0;
var ERR_GENERAL_ERROR = 101;
var ERR_SERVER_BUSY = 102;
var ERR_INVALID_ARGUMENT = 201;
var ERR_ELEMENT_CANNOT_HAVE_CHILDREN = 202;
var ERR_ELEMENT_IS_NOT_AN_ARRAY = 203;
var ERR_NOT_INITIALIZED = 301;
var ERR_Not_IMPLEMENTED = 401;
var ERR_INVALID_SET_VALUE = 402;
var ERR_ELEMENT_IS_READ_ONLY = 403;
var ERR_ELEMENT_IS_WRITE_ONLY = 404;
var ERR_INCORRECT_DATA_TYPE = 405;


// ----------------------------------------------------------------------------
// Initialize communication with LMS
function LMSInitialize()
{
    if (lmsInitCalled) {
        message("LMSInitialize() already called");
        return "true";
    }

    var api = getAPIHandle();
    if (api == null)
        return "false";

    var result = api.LMSInitialize("");
    if (result.toString() != "true") {
        error("LMSInitialize error");
        return "false";
    }

    message("LMSInitialize() succeeds.");
    lmsInitCalled = true;
    lmsFinishCalled = false;
    if (this.top.apiHandle) {
        this.top.lmsInitCalled = lmsInitCalled;
        this.top.lmsFinishCalled = lmsFinishCalled;
    }

    return result.toString();
}

// ----------------------------------------------------------------------------
// Close communication with LMS
function LMSFinish()
{
    if (lmsFinishCalled) {
        message("LMSFinish() already called");
        return "true";
    }

    var api = getAPIHandle();
    if (api == null)
        return "false";

    var result = api.LMSFinish("");
    if (result.toString() != "true") {
        error("LMSFinish error");
        return "false";
    }

    message("LMSFinish() succeeds.");
    lmsFinishCalled = true;
    lmsInitCalled = false;
    if (this.top.apiHandle) {
        this.top.lmsInitCalled = lmsInitCalled;
        this.top.lmsFinishCalled = lmsFinishCalled;
    }

    return result.toString();
}

// ----------------------------------------------------------------------------
//  Wraps the call to the LMS LMSGetValue method
function LMSGetValue(name)
{
    var api = getAPIHandle();
    if (api == null)
        return "";

    if (lmsFinishCalled == true) {
        message("Unable to perform LMSGetValue after LMSFinish already called");
        return "";
    }

    var value = api.LMSGetValue(name).toString();
    message('LMSGetValue for ' + name + " = " + value);
    return value;
}

// ----------------------------------------------------------------------------
// Wraps the call to the LMS LMSSetValue function
function LMSSetValue(name, value)
{
    var api = getAPIHandle();
    if (api == null)
        return;

    if (lmsFinishCalled == true) {
        message("Unable to perform LMSGetValue after LMSFinish already called");
        return;
    }

    var result = api.LMSSetValue(name, value);
    if (result.toString() != "true")
        error("LMSSetValue Error for " + name + " to [" + value + "]");
}

// ----------------------------------------------------------------------------
// Wraps the call to the LMS LMSCommit function
function LMSCommit()
{
    var api = getAPIHandle();
    if (api == null)
        return "false";

    if (lmsFinishCalled == true) {
        message("Unable to perform LMSGetValue after LMSFinish already called");
        return "false";
    }

    var result = api.LMSCommit("");
    if (result.toString() != "true")
        error("LMSCommit Error: ");

   return result.toString();
}

// ----------------------------------------------------------------------------
// The error code that was set by the last LMS function call
function LMSGetLastError()
{
    var api = getAPIHandle();
    if (api == null)
        return ERR_GENERAL_ERROR;

    return api.LMSGetLastError().toString();
}

// ----------------------------------------------------------------------------
// The textual description that corresponds to the input error code
function LMSGetErrorString(error)
{
    var api = getAPIHandle();
    if (api == null)
        return "General error";

    return api.LMSGetErrorString(error).toString();
}

// ----------------------------------------------------------------------------
// Call the LMSGetDiagnostic function
function LMSGetDiagnostic(error)
{
    var api = getAPIHandle();
    if (api == null)
        return "General error";

   return api.LMSGetDiagnostic(error).toString();
}

// ----------------------------------------------------------------------------
// true if the LMS API is currently initialized, otherwise false
// There is no direct method for determining if the LMS API is initialized
// for example an LMSIsInitialized function defined on the API so we'll try
// a simple LMSGetValue and trap for the LMS Not Initialized Error
function LMSIsInitialized()
{
    var api = getAPIHandle();
    if (api == null)
        return false;

    if (lmsFinishCalled == true )
        return false;

    var value = api.LMSGetValue("cmi.core.student_name");
    if (value.toString().length == 0) {
        var error = parseInt(api.LMSGetLastError().toString(), 10);
        if (error == ERR_NOT_INITIALIZED)
            return false;
    }
    return true;
}

// ----------------------------------------------------------------------------
// Returns the handle to API object
function getAPIHandle()
{
    if (apiHandle != null)
        return apiHandle;

    apiHandle = findAPI(window);
    if ((apiHandle == null) && (window.opener != null)
        && (typeof(window.opener) != "undefined")) {
        apiHandle = findAPI(window.opener);
    }

    if ((apiHandle == null) && (top.opener != null) && (top.opener.top != null)
        && (top.opener.top.opener != null)
        && (typeof(top.opener.top.opener) != "undefined"))
            apiHandle = findAPI(top.opener.top.opener);

    if (apiHandle == null)
        message("Unable to locate the LMS's API Implementation.");

    return apiHandle;
}

// ----------------------------------------------------------------------------
// If an API object is found, it's returned, otherwise null is returned
function findAPI(win)
{
    var findAPITries = 0;
    while ((win.API == null) && (win.parent != null) && (win.parent != win))
    {
        findAPITries++;
        if (findAPITries > 10)  {
            message("Error finding API -- too deeply nested.");
            return null;
        }

        win = win.parent;
    }

    return win.API;
}

// ----------------------------------------------------------------------------
// Display an error message thanks to log() function of global ouput object.
function error(msg)
{
    var api = getAPIHandle();
    if (api == null)
        return ERR_NOT_INITIALIZED;

    // Check for errors caused by or from the LMS
    var code = parseInt(api.LMSGetLastError().toString(), 10);
    if (code != ERR_NO_ERROR)
        message(msg + ": (" + code + ") " + api.LMSGetErrorString(code)
                + " [" + api.LMSGetDiagnostic(null) + "]");

    return code;
}

// ----------------------------------------------------------------------------
// Display a message thanks to log() function of global ouput object.
function message(msg)
{
    if (debug) console.log(msg);
}
