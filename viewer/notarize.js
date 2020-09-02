require('dotenv').config();
const { notarize } = require('electron-notarize');

module.exports = async function(context) {
  if (process.platform !== 'darwin') {
    return;
  }

  const appOutDir = context.appOutDir;
  const appName = context.packager.appInfo.productFilename;

  try {
    await notarize({
      appBundleId: 'com.goodhertz.coldtype',
      appPath: `${appOutDir}/${appName}.app`,
      appleId: process.env.APPLEID,
      appleIdPassword: process.env.APPLEIDPASS
    });
  } catch (err) {
    // console.log(err);
  }
};
