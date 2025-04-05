const { request, gql } = require('graphql-request');

const endpoint = 'https://gateway.thegraph.com/api/subgraphs/id/F3XjWNiNFUTbZhNQjXuhP7oDug2NaPwMPZ5XCRx46h5U';

const query = `{
  questions(where: {user: "0x2d2f90786a365a2044324f6861697e9EF341F858"}) 
  {
    data
  }
} `;

const headers = {
  Authorization: 'Bearer be5ddfca879e5ea553aa90060c35999a',
};

async function fetchData() {
  try {
    const data = await request(endpoint, query, {}, headers);
    console.log(data);
  } catch (error) {
    console.error('Error fetching data:', error);
  }
}

fetchData();
