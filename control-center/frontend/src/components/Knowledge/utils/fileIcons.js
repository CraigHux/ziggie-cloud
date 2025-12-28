import {
  Description,
  VideoLibrary,
  Code,
  Article,
  PictureAsPdf,
  Image as ImageIcon,
  Folder,
  InsertDriveFile,
  TextSnippet,
} from '@mui/icons-material';

/**
 * Get Material-UI icon component for file type
 * @param {string} fileType - The file type (document, video, code, etc.)
 * @returns {React.Component} Material-UI icon component
 */
export const getFileIcon = (fileType) => {
  const iconMap = {
    document: Description,
    video: VideoLibrary,
    code: Code,
    transcript: Article,
    pdf: PictureAsPdf,
    image: ImageIcon,
    folder: Folder,
    text: TextSnippet,
    markdown: Description,
  };
  return iconMap[fileType?.toLowerCase()] || InsertDriveFile;
};

/**
 * Get color for file type badge
 * @param {string} fileType - The file type
 * @returns {string} Material-UI color variant
 */
export const getFileColor = (fileType) => {
  const colorMap = {
    document: 'primary',
    video: 'secondary',
    code: 'success',
    transcript: 'info',
    pdf: 'error',
    image: 'warning',
    markdown: 'primary',
  };
  return colorMap[fileType?.toLowerCase()] || 'default';
};

/**
 * Format file size in human-readable format
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted size (e.g., "1.5 MB")
 */
export const formatFileSize = (bytes) => {
  if (!bytes || bytes === 0) return '--';

  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const k = 1024;
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${(bytes / Math.pow(k, i)).toFixed(1)} ${units[i]}`;
};

/**
 * Format date relative to now
 * @param {string|Date} date - Date to format
 * @returns {string} Formatted date (e.g., "2 hours ago" or "Jan 9, 2025")
 */
export const formatRelativeDate = (date) => {
  if (!date) return 'Not available';

  const now = new Date();
  const then = new Date(date);
  const diffMs = now - then;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

  // Format as "Jan 9, 2025"
  return then.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
};

/**
 * Get file extension from filename
 * @param {string} filename - The filename
 * @returns {string} File extension (lowercase, without dot)
 */
export const getFileExtension = (filename) => {
  if (!filename) return '';
  const parts = filename.split('.');
  return parts.length > 1 ? parts.pop().toLowerCase() : '';
};

/**
 * Truncate filename if too long
 * @param {string} filename - The filename
 * @param {number} maxLength - Maximum length before truncation
 * @returns {string} Truncated filename with ellipsis
 */
export const truncateFilename = (filename, maxLength = 40) => {
  if (!filename || filename.length <= maxLength) return filename;

  const ext = getFileExtension(filename);
  const nameWithoutExt = filename.slice(0, filename.length - ext.length - 1);
  const truncated = nameWithoutExt.slice(0, maxLength - ext.length - 4);

  return `${truncated}...${ext}`;
};
