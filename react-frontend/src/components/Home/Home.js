import React from 'react';
import styled from 'styled-components';
import SideBar from './SideBar'

const GridWrapper = styled.div`
  display: 
  grid-gap: 10px;
  margin-top: 1em;
  margin-left: 15em;
  margin-right: 6em;
  grid-template-columns: repeat(12, 1fr);
  grid-auto-rows: minmax(25px, auto);
`;
export const Home = (props) => (
  <div>
  <SideBar / >
  <GridWrapper>
  </GridWrapper>
  </div>
)


 

