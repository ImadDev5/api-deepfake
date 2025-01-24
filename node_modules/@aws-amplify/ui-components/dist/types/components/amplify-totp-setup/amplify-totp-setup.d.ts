import { CognitoUserInterface, AuthStateHandler } from '../../common/types/auth-types';
export declare class AmplifyTOTPSetup {
    private inputProps;
    /** Used in order to configure TOTP for a user */
    user: CognitoUserInterface;
    /** Auth state change handler for this component */
    handleAuthStateChange: AuthStateHandler;
    /** Used for header text in totp setup component */
    headerText: string;
    /** Used for customizing the issuer string in the qr code image */
    issuer: string;
    /** This is run after totp setup is complete. Useful if using this as standalone. */
    handleComplete: (user: CognitoUserInterface) => void | Promise<void>;
    /** Set this to true if this component is running outside the default `amplify-authenticator` usage */
    standalone: boolean;
    code: string | null;
    setupMessage: string | null;
    qrCodeImageSource: string;
    qrCodeInput: string | null;
    loading: boolean;
    private removeHubListener;
    componentWillLoad(): Promise<void>;
    /**
     * If this component is being used externally, we can use `@Watch` as normal.
     */
    handleUserChange(): void;
    disconnectedCallback(): void;
    private buildOtpAuthPath;
    private onTOTPEvent;
    private handleTotpInputChange;
    private generateQRCode;
    private setup;
    private verifyTotpToken;
    render(): any;
}
