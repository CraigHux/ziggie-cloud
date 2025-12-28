import { createTheme } from '@mui/material/styles';
import themeConfig from './theme.json';

// Create Material-UI theme from the Art Director's design system
export const createAppTheme = (mode = 'dark') => {
  // Select the appropriate theme configuration
  const themeData = mode === 'dark' ? themeConfig.darkTheme : themeConfig.lightTheme;

  return createTheme({
    palette: themeData.palette,
    typography: themeData.typography,
    shape: themeData.shape,
    spacing: themeData.spacing,
    shadows: themeData.shadows,
    components: themeData.components,
  });
};

// Export theme configuration for reference
export const themeConstants = {
  colors: themeConfig.colors,
  semantic: themeConfig.semantic,
  layout: themeConfig.layout,
  borderRadius: themeConfig.borderRadius,
};

export default createAppTheme;
