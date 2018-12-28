const fs = require('fs');
const path = require('path');
const webpack = require('webpack');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');

const viewsDir = path.resolve(process.cwd(), 'views');
const views = fs.readdirSync(viewsDir);

module.exports = {
  entry: function() {
    const entries = {};

    for (const view of views) {
      entries[view] = path.resolve(viewsDir, view, 'app.js');
    }

    return entries;
  }(),

  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            plugins: [
              ['@babel/plugin-transform-react-jsx', { pragma: 'm' }]
            ]
          }
        }
      },
      {
        test: /\.scss$/,
        exclude: /node_modules/,
        use: [
          { loader: MiniCssExtractPlugin.loader },
          { loader: 'css-loader' },
          { loader: 'sass-loader' }
        ]
      },
      {
        test:  /\.(png|jpg|gif|svg|woff2)$/,
        exclude: /node_modules/,
        use: 'file-loader'
      }
    ]
  },

  output: {
    filename: '[name].js',
    path: path.resolve(process.cwd(), 'dist'),
    publicPath: '',
    libraryTarget: 'window'
  },

  optimization: {
    splitChunks: {
      chunks: 'all',
      name: (module, chunks, cacheGroupKey) => cacheGroupKey
    }
  },

  plugins: [
    new MiniCssExtractPlugin({
      filename: '[name].css'
    }),
    ...views.map(view => {
      let templatePath = path.resolve(viewsDir, view, 'app.html');
      if (!fs.existsSync(templatePath))
        templatePath = path.resolve(__dirname, 'common', 'App.html');

      return new HtmlWebpackPlugin({
        filename: view + '.html',
        template: templatePath,
        chunks: ['vendors', view],
        inject: false
      })
    })
  ]
};
