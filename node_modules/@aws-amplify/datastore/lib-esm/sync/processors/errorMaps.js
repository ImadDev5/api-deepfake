var __read = (this && this.__read) || function (o, n) {
    var m = typeof Symbol === "function" && o[Symbol.iterator];
    if (!m) return o;
    var i = m.call(o), r, ar = [], e;
    try {
        while ((n === void 0 || n-- > 0) && !(r = i.next()).done) ar.push(r.value);
    }
    catch (error) { e = { error: error }; }
    finally {
        try {
            if (r && !r.done && (m = i["return"])) m.call(i);
        }
        finally { if (e) throw e.error; }
    }
    return ar;
};
var __spread = (this && this.__spread) || function () {
    for (var ar = [], i = 0; i < arguments.length; i++) ar = ar.concat(__read(arguments[i]));
    return ar;
};
var __values = (this && this.__values) || function(o) {
    var s = typeof Symbol === "function" && Symbol.iterator, m = s && o[s], i = 0;
    if (m) return m.call(o);
    if (o && typeof o.length === "number") return {
        next: function () {
            if (o && i >= o.length) o = void 0;
            return { value: o && o[i++], done: !o };
        }
    };
    throw new TypeError(s ? "Object is not iterable." : "Symbol.iterator is not defined.");
};
var connectionTimeout = function (error) {
    return /^Connection failed: Connection Timeout/.test(error.message);
};
var serverError = function (error) {
    return /^Error: Request failed with status code 5\d\d/.test(error.message);
};
export var mutationErrorMap = {
    BadModel: function () { return false; },
    BadRecord: function (error) {
        var message = error.message;
        return (/^Cannot return \w+ for [\w-_]+ type/.test(message) ||
            /^Variable '.+' has coerced Null value for NonNull type/.test(message)); // newly required field, out of date client
    },
    ConfigError: function () { return false; },
    Transient: function (error) { return connectionTimeout(error) || serverError(error); },
    Unauthorized: function (error) {
        return /^Request failed with status code 401/.test(error.message);
    },
};
export var subscriptionErrorMap = {
    BadModel: function () { return false; },
    BadRecord: function () { return false; },
    ConfigError: function () { return false; },
    Transient: function (observableError) {
        var error = unwrapObservableError(observableError);
        return connectionTimeout(error) || serverError(error);
    },
    Unauthorized: function (observableError) {
        var error = unwrapObservableError(observableError);
        return /Connection failed.+Unauthorized/.test(error.message);
    },
};
export var syncErrorMap = {
    BadModel: function () { return false; },
    BadRecord: function (error) { return /^Cannot return \w+ for [\w-_]+ type/.test(error.message); },
    ConfigError: function () { return false; },
    Transient: function (error) { return connectionTimeout(error) || serverError(error); },
    Unauthorized: function () { return false; },
};
/**
 * Get the first error reason of an observable.
 * Allows for error maps to be easily applied to observable errors
 *
 * @param observableError an error from ZenObservable subscribe error callback
 */
function unwrapObservableError(observableError) {
    var _a = observableError.error, _b = __read((_a === void 0 ? {
        errors: [],
    } : _a).errors, 1), error = _b[0];
    return error;
}
export function getMutationErrorType(error) {
    return mapErrorToType(mutationErrorMap, error);
}
export function getSubscriptionErrorType(error) {
    return mapErrorToType(subscriptionErrorMap, error);
}
export function getSyncErrorType(error) {
    return mapErrorToType(syncErrorMap, error);
}
/**
 * Categorizes an error with a broad error type, intended to make
 * customer error handling code simpler.
 * @param errorMap Error names and a list of patterns that indicate them (each pattern as a regex or function)
 * @param error The underying error to categorize.
 */
export function mapErrorToType(errorMap, error) {
    var e_1, _a;
    var errorTypes = __spread(Object.keys(errorMap));
    try {
        for (var errorTypes_1 = __values(errorTypes), errorTypes_1_1 = errorTypes_1.next(); !errorTypes_1_1.done; errorTypes_1_1 = errorTypes_1.next()) {
            var errorType = errorTypes_1_1.value;
            var matcher = errorMap[errorType];
            if (matcher(error)) {
                return errorType;
            }
        }
    }
    catch (e_1_1) { e_1 = { error: e_1_1 }; }
    finally {
        try {
            if (errorTypes_1_1 && !errorTypes_1_1.done && (_a = errorTypes_1.return)) _a.call(errorTypes_1);
        }
        finally { if (e_1) throw e_1.error; }
    }
    return 'Unknown';
}
//# sourceMappingURL=errorMaps.js.map