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
 * Copyright 2017-2022 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
var client_lex_runtime_v2_1 = require("@aws-sdk/client-lex-runtime-v2");
var core_1 = require("@aws-amplify/core");
var utils_1 = require("./AWSLexProviderHelper/utils");
var commonUtils_1 = require("./AWSLexProviderHelper/commonUtils");
var logger = new core_1.ConsoleLogger('AWSLexV2Provider');
var AWSLexV2Provider = /** @class */ (function (_super) {
    __extends(AWSLexV2Provider, _super);
    /**
     * Initialize Interactions with AWS configurations
     * @param {InteractionsOptions} options - Configuration object for Interactions
     */
    function AWSLexV2Provider(options) {
        if (options === void 0) { options = {}; }
        var _this = _super.call(this, options) || this;
        _this._botsCompleteCallback = {};
        return _this;
    }
    /**
     * get provider name of the plugin
     * @returns {string} name of the provider
     */
    AWSLexV2Provider.prototype.getProviderName = function () {
        return 'AWSLexV2Provider';
    };
    /**
     * Configure Interactions part with aws configuration
     * @param {AWSLexV2ProviderOptions} config - Configuration of the Interactions
     * @return {AWSLexV2ProviderOptions} - Current configuration
     */
    AWSLexV2Provider.prototype.configure = function (config) {
        if (config === void 0) { config = {}; }
        var propertiesToTest = [
            'name',
            'botId',
            'aliasId',
            'localeId',
            'providerName',
            'region',
        ];
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
     * Send a message to a bot
     * @async
     * @param {string} botname - Bot name to send the message
     * @param {string | InteractionsMessage} message - message to send to the bot
     * @return {Promise<InteractionsResponse>} A promise resolves to the response from the bot
     */
    AWSLexV2Provider.prototype.sendMessage = function (botname, message) {
        return __awaiter(this, void 0, void 0, function () {
            var credentials, error_1, response, reqBaseParams;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        // check if bot exists
                        if (!this._config[botname]) {
                            return [2 /*return*/, Promise.reject('Bot ' + botname + ' does not exist')];
                        }
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        return [4 /*yield*/, core_1.Credentials.get()];
                    case 2:
                        credentials = _a.sent();
                        return [3 /*break*/, 4];
                    case 3:
                        error_1 = _a.sent();
                        return [2 /*return*/, Promise.reject('No credentials')];
                    case 4:
                        this._lexRuntimeServiceV2Client = new client_lex_runtime_v2_1.LexRuntimeV2Client({
                            region: this._config[botname].region,
                            credentials: credentials,
                            customUserAgent: core_1.getAmplifyUserAgent(),
                        });
                        reqBaseParams = {
                            botAliasId: this._config[botname].aliasId,
                            botId: this._config[botname].botId,
                            localeId: this._config[botname].localeId,
                            sessionId: credentials.identityId,
                        };
                        if (!(typeof message === 'string')) return [3 /*break*/, 6];
                        return [4 /*yield*/, this._handleRecognizeTextCommand(botname, message, reqBaseParams)];
                    case 5:
                        response = _a.sent();
                        return [3 /*break*/, 8];
                    case 6: return [4 /*yield*/, this._handleRecognizeUtteranceCommand(botname, message, reqBaseParams)];
                    case 7:
                        response = _a.sent();
                        _a.label = 8;
                    case 8: return [2 /*return*/, response];
                }
            });
        });
    };
    /**
     * Attach a onComplete callback function to a bot.
     * The callback is called once the bot's intent is fulfilled
     * @param {string} botname - Bot name to attach the onComplete callback
     * @param {(err: Error | null, confirmation: InteractionsResponse) => void} callback - called when Intent Fulfilled
     */
    AWSLexV2Provider.prototype.onComplete = function (botname, callback) {
        // does bot exist
        if (!this._config[botname]) {
            throw new Error('Bot ' + botname + ' does not exist');
        }
        this._botsCompleteCallback[botname] = callback;
    };
    /**
     * @private
     * call onComplete callback for a bot if configured
     */
    AWSLexV2Provider.prototype._reportBotStatus = function (data, botname) {
        var _this = this;
        var _a, _b, _c, _d, _e, _f;
        var sessionState = data === null || data === void 0 ? void 0 : data.sessionState;
        // Check if state is fulfilled to resolve onFullfilment promise
        logger.debug('postContent state', (_a = sessionState === null || sessionState === void 0 ? void 0 : sessionState.intent) === null || _a === void 0 ? void 0 : _a.state);
        var isConfigOnCompleteAttached = typeof ((_b = this._config) === null || _b === void 0 ? void 0 : _b[botname].onComplete) === 'function';
        var isApiOnCompleteAttached = typeof ((_c = this._botsCompleteCallback) === null || _c === void 0 ? void 0 : _c[botname]) === 'function';
        // no onComplete callbacks added
        if (!isConfigOnCompleteAttached && !isApiOnCompleteAttached)
            return;
        if (((_d = sessionState === null || sessionState === void 0 ? void 0 : sessionState.intent) === null || _d === void 0 ? void 0 : _d.state) === 'ReadyForFulfillment' ||
            ((_e = sessionState === null || sessionState === void 0 ? void 0 : sessionState.intent) === null || _e === void 0 ? void 0 : _e.state) === 'Fulfilled') {
            if (isApiOnCompleteAttached) {
                setTimeout(function () { var _a; return (_a = _this._botsCompleteCallback) === null || _a === void 0 ? void 0 : _a[botname](null, data); }, 0);
            }
            if (isConfigOnCompleteAttached) {
                setTimeout(function () { return _this._config[botname].onComplete(null, data); }, 0);
            }
        }
        if (((_f = sessionState === null || sessionState === void 0 ? void 0 : sessionState.intent) === null || _f === void 0 ? void 0 : _f.state) === 'Failed') {
            var error_2 = new Error('Bot conversation failed');
            if (isApiOnCompleteAttached) {
                setTimeout(function () { return _this._botsCompleteCallback[botname](error_2); }, 0);
            }
            if (isConfigOnCompleteAttached) {
                setTimeout(function () { return _this._config[botname].onComplete(error_2); }, 0);
            }
        }
    };
    /**
     * Format UtteranceCommandOutput's response
     * decompress attributes
     * update audioStream format
     */
    AWSLexV2Provider.prototype._formatUtteranceCommandOutput = function (data) {
        return __awaiter(this, void 0, void 0, function () {
            var response, _a, _b, _c;
            return __generator(this, function (_d) {
                switch (_d.label) {
                    case 0:
                        _a = [__assign({}, data)];
                        _b = {};
                        return [4 /*yield*/, commonUtils_1.unGzipBase64AsJson(data.messages)];
                    case 1:
                        _b.messages = _d.sent();
                        return [4 /*yield*/, commonUtils_1.unGzipBase64AsJson(data.sessionState)];
                    case 2:
                        _b.sessionState = _d.sent();
                        return [4 /*yield*/, commonUtils_1.unGzipBase64AsJson(data.interpretations)];
                    case 3:
                        _b.interpretations = _d.sent();
                        return [4 /*yield*/, commonUtils_1.unGzipBase64AsJson(data.requestAttributes)];
                    case 4:
                        _b.requestAttributes = _d.sent();
                        return [4 /*yield*/, commonUtils_1.unGzipBase64AsJson(data.inputTranscript)];
                    case 5:
                        _b.inputTranscript = _d.sent();
                        if (!data.audioStream) return [3 /*break*/, 7];
                        return [4 /*yield*/, utils_1.convert(data.audioStream)];
                    case 6:
                        _c = _d.sent();
                        return [3 /*break*/, 8];
                    case 7:
                        _c = undefined;
                        _d.label = 8;
                    case 8:
                        response = __assign.apply(void 0, _a.concat([(_b.audioStream = _c, _b)]));
                        return [2 /*return*/, response];
                }
            });
        });
    };
    /**
     * handle client's `RecognizeTextCommand`
     * used for sending simple text message
     */
    AWSLexV2Provider.prototype._handleRecognizeTextCommand = function (botname, data, baseParams) {
        return __awaiter(this, void 0, void 0, function () {
            var params, recognizeTextCommand, data_1, err_1;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        logger.debug('postText to lex2', data);
                        params = __assign(__assign({}, baseParams), { text: data });
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        recognizeTextCommand = new client_lex_runtime_v2_1.RecognizeTextCommand(params);
                        return [4 /*yield*/, this._lexRuntimeServiceV2Client.send(recognizeTextCommand)];
                    case 2:
                        data_1 = _a.sent();
                        this._reportBotStatus(data_1, botname);
                        return [2 /*return*/, data_1];
                    case 3:
                        err_1 = _a.sent();
                        return [2 /*return*/, Promise.reject(err_1)];
                    case 4: return [2 /*return*/];
                }
            });
        });
    };
    /**
     * handle client's `RecognizeUtteranceCommand`
     * used for obj text or obj voice message
     */
    AWSLexV2Provider.prototype._handleRecognizeUtteranceCommand = function (botname, data, baseParams) {
        return __awaiter(this, void 0, void 0, function () {
            var content, messageType, params, inputStream, _a, recognizeUtteranceCommand, data_2, response, err_2;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        content = data.content, messageType = data.options.messageType;
                        logger.debug('postContent to lex2', data);
                        if (!(messageType === 'voice')) return [3 /*break*/, 4];
                        if (typeof content !== 'object') {
                            return [2 /*return*/, Promise.reject('invalid content type')];
                        }
                        if (!(content instanceof Uint8Array)) return [3 /*break*/, 1];
                        _a = content;
                        return [3 /*break*/, 3];
                    case 1: return [4 /*yield*/, utils_1.convert(content)];
                    case 2:
                        _a = _b.sent();
                        _b.label = 3;
                    case 3:
                        inputStream = _a;
                        params = __assign(__assign({}, baseParams), { requestContentType: 'audio/x-l16; sample-rate=16000; channel-count=1', inputStream: inputStream });
                        return [3 /*break*/, 5];
                    case 4:
                        // text input
                        if (typeof content !== 'string')
                            return [2 /*return*/, Promise.reject('invalid content type')];
                        params = __assign(__assign({}, baseParams), { requestContentType: 'text/plain; charset=utf-8', inputStream: content });
                        _b.label = 5;
                    case 5:
                        _b.trys.push([5, 8, , 9]);
                        recognizeUtteranceCommand = new client_lex_runtime_v2_1.RecognizeUtteranceCommand(params);
                        return [4 /*yield*/, this._lexRuntimeServiceV2Client.send(recognizeUtteranceCommand)];
                    case 6:
                        data_2 = _b.sent();
                        return [4 /*yield*/, this._formatUtteranceCommandOutput(data_2)];
                    case 7:
                        response = _b.sent();
                        this._reportBotStatus(response, botname);
                        return [2 /*return*/, response];
                    case 8:
                        err_2 = _b.sent();
                        return [2 /*return*/, Promise.reject(err_2)];
                    case 9: return [2 /*return*/];
                }
            });
        });
    };
    return AWSLexV2Provider;
}(InteractionsProvider_1.AbstractInteractionsProvider));
exports.AWSLexV2Provider = AWSLexV2Provider;
//# sourceMappingURL=AWSLexV2Provider.js.map