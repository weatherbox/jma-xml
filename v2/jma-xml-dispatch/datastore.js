const Datastore = require('@google-cloud/datastore');
const projectId = 'weatherbox-217409';
const datastore = new Datastore({ projectId });
const lastIdKey = datastore.key(['jma-xml-last-update', 'last-id']);


init();

async function init() {
  const entity = {
    key: lastIdKey,
    data: [
      {
        name: 'lastId',
        value: '',
        excludeFromIndexes: true,
      }
    ]
  };

  try {
    await datastore.save(entity);
    console.log('created successfully.');
  } catch (err) {
    console.error('ERROR:', err);
  }
}

