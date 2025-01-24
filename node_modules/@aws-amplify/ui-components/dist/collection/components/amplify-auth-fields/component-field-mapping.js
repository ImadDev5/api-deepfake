import { h } from '@stencil/core';
const componentFieldMapping = {
    username: (ff) => (h("amplify-username-field", { label: ff.label, placeholder: ff.placeholder, required: ff.required, handleInputChange: ff.handleInputChange, value: ff.value, inputProps: ff.inputProps, disabled: ff.disabled, hint: ff.hint })),
    password: (ff) => (h("amplify-password-field", { label: ff.label, placeholder: ff.placeholder, hint: ff.hint, required: ff.required, handleInputChange: ff.handleInputChange, value: ff.value, inputProps: ff.inputProps, disabled: ff.disabled })),
    email: (ff) => (h("amplify-email-field", { label: ff.label, placeholder: ff.placeholder, required: ff.required, handleInputChange: ff.handleInputChange, value: ff.value, inputProps: ff.inputProps, disabled: ff.disabled, hint: ff.hint })),
    code: (ff) => (h("amplify-code-field", { label: ff.label, placeholder: ff.placeholder, hint: ff.hint, required: ff.required, handleInputChange: ff.handleInputChange, value: ff.value, inputProps: Object.assign(Object.assign({}, ff.inputProps), { min: '0' }), disabled: ff.disabled })),
    // TODO: Will create a phone field component once the dial country code component is in
    phone_number: (ff) => (h("amplify-phone-field", { label: ff.label, placeholder: ff.placeholder, required: ff.required, handleInputChange: ff.handleInputChange, value: ff.value, inputProps: ff.inputProps, disabled: ff.disabled, dialCode: ff.dialCode, hint: ff.hint })),
    default: (ff) => (h("amplify-form-field", { label: ff.label, type: ff.type, placeholder: ff.placeholder, required: ff.required, handleInputChange: ff.handleInputChange, value: ff.value, inputProps: ff.inputProps, disabled: ff.disabled, hint: ff.hint })),
};
export default componentFieldMapping;
