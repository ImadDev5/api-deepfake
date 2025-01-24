import { AccessLevel } from '../../common/types/storage-types';
export declare class AmplifyS3Image {
    /** The key of the image object in S3 */
    imgKey: string;
    /** String representing directory location to image file */
    path: string;
    /** String representing the alternate image text */
    alt: string;
    /** Image body content to be uploaded */
    body: object;
    /** The content type header used when uploading to S3 */
    contentType: string;
    /** The access level of the image */
    level: AccessLevel;
    /** Whether or not to use track on get/put of the image */
    track: boolean;
    /** Cognito identity id of the another user's image */
    identityId: string;
    /** Function executed when image loads */
    handleOnLoad: (event: Event) => void;
    /** Function executed when error occurs for the image */
    handleOnError: (event: Event) => void;
    /** Attributes to be placed on the img element: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img#attributes */
    imgProps?: Record<PropertyKey, any>;
    /** Source for the image */
    src: string | object;
    watchHandler(): Promise<void>;
    componentWillLoad(): Promise<void>;
    private load;
    render(): any;
}
