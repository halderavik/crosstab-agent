module.exports = {
  presets: [
    ['next/babel', {
      'preset-react': {
        runtime: 'automatic',
        importSource: '@babel/runtime',
      },
    }],
    '@babel/preset-typescript',
  ],
  plugins: [
    '@babel/plugin-transform-runtime',
    '@babel/plugin-transform-class-properties',
    '@babel/plugin-transform-object-rest-spread',
  ],
}; 