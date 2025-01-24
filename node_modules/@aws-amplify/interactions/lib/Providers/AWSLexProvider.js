"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
/*
 * Copyright 2017-2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with
 * the License. A copy of the License is located at
 *
 *     http://aws.amazon.com/apache2.0/
 *
 * or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
 * CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions
 * and limitations under the License.
 */
var InteractionsProvider_1 = require("./InteractionsProvider");
var client_lex_runtime_service_1 = require("@aws-sdk/client-lex-runtime-service");
var core_1 = require("@aws-amplify/core");
var utils_1 = require("./AWSLexProviderHelper/utils");
var logger = new core_1.ConsoleLogger('AWSLexProvider');
var AWSLexProvider = /** @class */ (function (_super) {
    __extends(AWSLexProvider, _super);
    function AWSLexProvider(options) {
        if (options === void 0) { options = {}; }
        var _this = _super.call(this, options) || this;
        _this._botsCompleteCallback = {};
        return _this;
    }
    AWSLexProvider.prototype.getProviderName = function () {
        return 'AWSLexProvider';
    };
    AWSLexProvider.prototype.configure = function (config) {
        if (config === void 0) { config = {}; }
        var propertiesToTest = ['name', 'alias', 'region'];
        Object.keys(config).forEach(function (botKey) {
            var botConfig = config[botKey];
            // is bot config correct
            if (!propertiesToTest.every(function (x) { return x in botConfig; })) {
                throw new Error('invalid bot configuration');
            }
        });
        return _super.prototype.configure.call(this, config);
    };
    /**
     * @private
     * @deprecated
     * This is used internally by 'sendMessage' to call onComplete callback
     * for a bot if configured
     */
    AWSLexProvider.prototype.reportBotStatus = function (data, botname) {
        var _this = this;
        // Check if state is fulfilled to resolve onFullfilment promise
        logger.debug('postContent state', data.dialogState);
        if (data.dialogState === 'ReadyForFulfillment' ||
            data.dialogState === 'Fulfilled') {
            if (typeof this._botsCompleteCallback[botname] === 'function') {
                setTimeout(function () { return _this._botsCompleteCallback[botname](null, data); }, 0);
            }
            if (this._config &&
                typeof this._config[botname].onComplete === 'function') {
                setTimeout(function () { return _this._config[botname].onComplete(null, data); }, 0);
            }
        }
        if (data.dialogState === 'Failed') {
            if (typeof this._botsCompleteCallback[botname] === 'function') {
                setTimeout(function () { return _this._botsCompleteCallback[botname]('Bot conversation failed'); }, 0);
            }
            if (this._config &&
                typeof this._config[botname].onComplete === 'function') {
                setTimeout(function () { return _this._config[botname].onComplete('Bot conversation failed'); }, 0);
            }
        }
    };
    AWSLexProvider.prototype.sendMessage = function (botname, message) {
        return __awaiter(this, void 0, void 0, function () {
            var credentials, error_1, params, postTextCommand, data, err_1, content, messageType, inputStream, _a, postContentCommand, data, audioArray, _b, response, err_2;
            return __generator(this, function (_c) {
                switch (_c.label) {
                    case 0:
                        // check if bot exists
                        if (!this._config[botname]) {
                            return [2 /*return*/, Promise.reject('Bot ' + botname + ' does not exist')];
                        }
                        _c.label = 1;
                    case 1:
                        _c.trys.push([1, 3, , 4]);
                        return [4 /*yield*/, core_1.Credentials.get()];
                    case 2:
                        credentials = _c.sent();
                        return [3 /*break*/, 4];
                    case 3:
                        error_1 = _c.sent();
                        return [2 /*return*/, Promise.reject('No credentials')];
                    case 4:
                        this.lexRuntimeServiceClient = new client_lex_runtime_service_1.LexRuntimeServiceClient({
                            region: this._config[botname].region,
                            credentials: credentials,
                            customUserAgent: core_1.getAmplifyUserAgent(),
                        });
                        if (!(typeof message === 'string')) return [3 /*break*/, 9];
                        params = {
                            botAlias: this._config[botname].alias,
                            botName: botname,
                            inputText: message,
                            userId: credentials.identityId,
                        };
                        logger.debug('postText to lex', message);
                        _c.label = 5;
                    case 5:
                        _c.trys.push([5, 7, , 8]);
                        postTextCommand = new client_lex_runtime_service_1.PostTextCommand(params);
                        return [4 /*yield*/, this.lexRuntimeServiceClient.send(postTextCommand)];
                    case 6:
                        data = _c.sent();
                        this.reportBotStatus(data, botname);
                        return [2 /*return*/, data];
                    case 7:
                        err_1 = _c.sent();
                        return [2 /*return*/, Promise.reject(err_1)];
                    case 8: return [3 /*break*/, 21];
                    case 9:
                        content = message.content, messageType = message.options.messageType;
                        if (!(messageType === 'voice')) return [3 /*break*/, 13];
                        if (typeof content !== 'object') {
                            return [2 /*return*/, Promise.reject('invalid content type')];
                        }
                        if (!(content instanceof Uint8Array)) return [3 /*break*/, 10];
                        _a = content;
                        return [3 /*break*/, 12];
                    case 10: return [4 /*yield*/, utils_1.convert(content)];
                    case 11:
                        _a = _c.sent();
                        _c.label = 12;
                    case 12:
                        inputStream = _a;
                        params = {
                            botAlias: this._config[botname].alias,
                            botName: botname,
                            contentType: 'audio/x-l16; sample-rate=16000; channel-count=1',
                            userId: credentials.identityId,
                            accept: 'audio/mpeg',
                            inputStream: inputStream,
                        };
                        return [3 /*break*/, 14];
                    case 13:
                        if (typeof content !== 'string')
                            return [2 /*return*/, Promise.reject('invalid content type')];
                        params = {
                            botAlias: this._config[botname].alias,
                            botName: botname,
                            contentType: 'text/plain; charset=utf-8',
                            inputStream: content,
                            userId: credentials.identityId,
                            accept: 'audio/mpeg',
                        };
                        _c.label = 14;
                    case 14:
                        logger.debug('postContent to lex', message);
                        _c.label = 15;
                    case 15:
                        _c.trys.push([15, 20, , 21]);
                        postContentCommand = new client_lex_runtime_service_1.PostContentCommand(params);
                        return [4 /*yield*/, this.lexRuntimeServiceClient.send(postContentCommand)];
                    case 16:
                        data = _c.sent();
                        if (!data.audioStream) return [3 /*break*/, 18];
                        return [4 /*yield*/, utils_1.convert(data.audioStream)];
                    case 17:
                        _b = _c.sent();
                        return [3 /*break*/, 19];
                    case 18:
                        _b = undefined;
                        _c.label = 19;
                    case 19:
                        audioArray = _b;
                        response = __assign(__assign({}, data), { audioStream: audioArray });
                        this.reportBotStatus(response, botname);
                        return [2 /*return*/, response];
                    case 20:
                        err_2 = _c.sent();
                        return [2 /*return*/, Promise.reject(err_2)];
                    case 21: return [2 /*return*/];
                }
            });
        });
    };
    AWSLexProvider.prototype.onComplete = function (botname, callback) {
        // does bot exist
        if (!this._config[botname]) {
            throw new Error('Bot ' + botname + ' does not exist');
        }
        this._botsCompleteCallback[botname] = callback;
    };
    return AWSLexProvider;
}(InteractionsProvider_1.AbstractInteractionsProvider));
exports.AWSLexProvider = AWSLexProvider;
//# sourceMappingURL=AWSLexProvider.js.map