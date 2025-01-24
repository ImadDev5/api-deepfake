// Dictionaries
// fieldId constants
var USERNAME_SUFFIX = 'username';
var EMAIL_SUFFIX = 'email';
var CODE_SUFFIX = 'code';
var PHONE_SUFFIX = 'phone';
var PASSWORD_SUFFIX = 'password';
// Country Dial Code common constants
var COUNTRY_DIAL_CODE_SUFFIX = 'country-dial-code-select';
var COUNTRY_DIAL_CODE_DEFAULT = '+1';
// Auth Keys
var AUTH_SOURCE_KEY = 'amplify-auth-source';
// Error message Common Constants
var PHONE_EMPTY_ERROR_MESSAGE = 'Phone number can not be empty';
var NO_AUTH_MODULE_FOUND = 'No Auth module found, please ensure @aws-amplify/auth is imported';
var NO_STORAGE_MODULE_FOUND = 'No Storage module found, please ensure @aws-amplify/storage is imported';
var NO_INTERACTIONS_MODULE_FOUND = 'No Interactions module found, please ensure @aws-amplify/interactions is imported';
// Select MFA Types Messages
var USER_NOT_SETUP_SOFTWARE_TOKEN_MFA = 'User has not set up software token mfa';
var USER_NOT_VERIFIED_SOFTWARE_TOKEN_MFA = 'User has not verified software token mfa';
// Hub Events and Channels
var AUTH_CHANNEL = 'auth';
var UI_AUTH_CHANNEL = 'UI Auth';
var TOAST_AUTH_ERROR_EVENT = 'ToastAuthError';
var AUTH_STATE_CHANGE_EVENT = 'AuthStateChange';
export { AUTH_CHANNEL as A, COUNTRY_DIAL_CODE_SUFFIX as C, EMAIL_SUFFIX as E, NO_AUTH_MODULE_FOUND as N, PHONE_EMPTY_ERROR_MESSAGE as P, TOAST_AUTH_ERROR_EVENT as T, UI_AUTH_CHANNEL as U, AUTH_STATE_CHANGE_EVENT as a, PHONE_SUFFIX as b, NO_INTERACTIONS_MODULE_FOUND as c, NO_STORAGE_MODULE_FOUND as d, USER_NOT_SETUP_SOFTWARE_TOKEN_MFA as e, USER_NOT_VERIFIED_SOFTWARE_TOKEN_MFA as f, COUNTRY_DIAL_CODE_DEFAULT as g, AUTH_SOURCE_KEY as h, CODE_SUFFIX as i, PASSWORD_SUFFIX as j, USERNAME_SUFFIX as k };
