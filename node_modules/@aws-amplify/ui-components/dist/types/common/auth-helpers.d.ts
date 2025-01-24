import { CognitoUserInterface, AuthStateHandler, UsernameAliasStrings } from './types/auth-types';
export declare function checkContact(user: CognitoUserInterface, handleAuthStateChange: AuthStateHandler): Promise<void>;
export declare const handleSignIn: (username: string, password: string, handleAuthStateChange: AuthStateHandler, usernameAlias?: UsernameAliasStrings) => Promise<void>;
export declare const isCognitoUser: (user: CognitoUserInterface) => boolean;
