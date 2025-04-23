export const API_URL = process.env.NEXT_PUBLIC_API_URL;
export const WS_URL = process.env.NEXT_PUBLIC_WS_URL;
export const MAX_FILE_SIZE = parseInt(process.env.NEXT_PUBLIC_MAX_FILE_SIZE || '16777216');
export const SUPPORTED_CHART_TYPES = ['bar', 'line', 'pie', 'scatter', 'heatmap', 'box'];
export const SUPPORTED_EXPORT_FORMATS = ['csv', 'excel', 'png']; 