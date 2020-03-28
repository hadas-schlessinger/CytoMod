import React, { Component } from 'react'
import { Menu, Segment } from 'semantic-ui-react'
import InternalSideBar from './InternalSideBar'
import beckgroungTransperant from '../../beckgroungTransperant.png'

export default class NevigationAbsAdj extends Component {
  state = { activeItem: 'Absolute Cytokines' }

  handleItemClick = (e, { name }) => this.setState({ activeItem: name })

  render() {
    const { activeItem } = this.state

    return (
      <div >
        <Menu pointing secondary>
          <Menu.Item
            name='Absolute Cytokines'
            active={activeItem === 'Absolute Cytokines'}
            onClick={this.handleItemClick}
          />
          <Menu.Item
            name='Adjusted Cytokines'
            active={activeItem === 'Adjusted Cytokines'}
            onClick={this.handleItemClick}
          />
        </Menu>
      
      </div>
    )
  }
}