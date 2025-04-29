import React, { useState } from 'react'
import Accordion from './Accordion'
import AccordionItem from './AccordionItem'
import villagers from '../villagers.json'

const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const toggle = () => setIsOpen(!isOpen);

  const invisSources = ['6 Homes and School', 'Start', 'From player catalog after 27th home'];
  const facilities = ['School','Cafe','Restaurant','Hospital','Apparel Shop','Leif Lesson'];

  const onlyVillagers = villagers.filter((villager) => !(invisSources.includes(villager.Name) | facilities.includes(villager.Name)));
  const onlyFacilities = villagers.filter((villager) => facilities.includes(villager.Name));

  return (
    <div className="sidebar">
      <button className="sidebar-toggle" onClick={toggle}>
        <svg width="32px" height="32px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M4 18L20 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M4 12L20 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M4 6L20 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </button>

      <div className={`checklist ${isOpen ? 'open' : ''}`}>
        <h2>Checklist</h2>

        <div className="villagers">
          <Accordion
            title="Villagers"
            data={onlyVillagers.map((villager) => (
              <AccordionItem source={villager} />
            ))}
          />
        </div>

        <div className="facilities">
          <Accordion
            title="Facilities & Milestones"
            data={onlyFacilities.map((villager) => (
              <AccordionItem source={villager} />
            ))}
          />
        </div>

        <button className="checklist-button">
          Placeholder button
        </button>
      </div>
    </div>
  )
}

export default Sidebar
