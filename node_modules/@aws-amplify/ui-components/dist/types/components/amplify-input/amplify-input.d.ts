import { TextFieldTypes, InputEvent } from '../../common/types/ui-types';
export declare class AmplifyInput {
    /** The ID of the field.  Should match with its corresponding input's ID. */
    fieldId: string;
    /** The text of the description.  Goes just below the label. */
    description: string | null;
    /** The input type.  Can be any HTML input type. */
    type?: TextFieldTypes;
    /** The callback, called when the input is modified by the user. */
    handleInputChange?: (inputEvent: InputEvent) => void;
    /** (Optional) The placeholder for the input element.  Using hints is recommended, but placeholders can also be useful to convey information to users. */
    placeholder?: string;
    /** (Optional) String value for the name of the input. */
    name?: string;
    /** The value of the content inside of the input field */
    value: string;
    /** Attributes places on the input element: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#Attributes */
    inputProps?: object;
    /** Will disable the input if set to true */
    disabled?: boolean;
    /** Whether the input is a required field */
    required?: boolean;
    /** Whether the input has been autocompleted */
    autoCompleted: boolean;
    private removeHubListener;
    el: HTMLAmplifyInputElement;
    /**
     * Sets the value of this input to the value in autofill input event.
     */
    private setAutoCompleteValue;
    /**
     * Checks if the target dummy input in `amplify-auth-container` is present have been autofilled.
     * If so, we update this.value with the autofilled value.
     */
    private checkAutoCompletion;
    disconnectedCallback(): void;
    componentWillLoad(): void;
    componentDidLoad(): void;
    render(): any;
}
