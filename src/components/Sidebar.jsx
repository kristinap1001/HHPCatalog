import React, { useState, useEffect } from 'react'
import Accordion from './Accordion'
import AccordionItem from './AccordionItem'
import villagers from '../villagers.json'

const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [about, setAbout] = useState(false);
  const [remaining, setRemaining] = useState(false);

  const handleClick = (event) => {
    const clickedSidebar = event.target.closest('.checklist.open') || event.target.closest('.sidebar-toggle');
    const clickedOverlay = event.target.closest('.overlay');
  
    if (isOpen && !clickedSidebar) {
      setIsOpen(false);
    }
  
    if ((about || remaining) && !clickedOverlay) {
      setAbout(false);
      setRemaining(false);
    }
  };
  
  useEffect(() => {
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [isOpen, about, remaining]);

  const invisSources = ['6 Homes and School', 'Start', 'From player catalog after 27th home'];
  const facilities = ['School','Cafe','Restaurant','Hospital','Apparel Shop','Leif Lesson'];

  const onlyVillagers = villagers.filter((villager) => !(invisSources.includes(villager.Name) | facilities.includes(villager.Name)));
  const onlyFacilities = villagers.filter((villager) => facilities.includes(villager.Name));

  return (
    <div className="sidebar">
      <button className="sidebar-toggle" onClick={() => setIsOpen(!isOpen)}>
        <svg width="32px" height="32px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M4 18L20 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          <path d="M4 12L20 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          <path d="M4 6L20 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
        </svg>
      </button>

      <div className={`checklist ${isOpen ? 'open' : ''}`}>
        <h2>Checklist</h2>

        <div className="villagers">
          <Accordion
            title="Villagers"
            data={onlyVillagers.map((villager) => (
              <AccordionItem source={villager} key={villager.Name}/>
            ))}
          />
        </div>

        <div className="facilities">
          <Accordion
            title="Facilities & Milestones"
            data={onlyFacilities.map((villager) => (
              <AccordionItem source={villager} key={villager.Name}/>
            ))}
          />
        </div>
        
        <div className="checklist-buttons">
          <button className="checklist-button" onClick={() => setAbout(!about)}>
            About
          </button>
          {about && <div className="overlay-background">
            <div className="overlay">
              <h3>Welcome to Happy Home Catalog!</h3>
              <p>
                This app allows you to track your unlocked furniture items in the Happy Home Paradise DLC for Animal Crossing: New Horizons. The purpose of this app is to display item unlocks for every villager and facility in one convenient place, making it easier to find and unlock all remaining items. Other Happy Home Paradise features and milestones, such as soundscapes, bugs, and pillars/counters, are outside the scope of this project.
              </p>
              <p>
                After selecting all of the villager homes and facilities you've designed in the checklist on the left, you can see at a glance which items are unlocked for future designs. These items can also be purchased from <em>Wardell</em> (excluding items that can't be bought from the Nook Shopping catalog, such as DIY or event items). You can click on an item to view more details and add it to your Favorites list.
              </p>
              <p>
                This app was made possible thanks to the <a target='_blank' href="https://tinyurl.com/acnh-sheet">ACNH Spreadsheet Project</a>, <a target='_blank' href="https://nookipedia.com">Nookipedia</a>, Stoney9215's <a target='_blank' href="https://docs.google.com/spreadsheets/d/1xifIDl8gwjzleKx3XWFynEHTcSJ4jA8qQ-uFlRsSu8A/edit?usp=sharing">HHP spreadsheets</a>, and chibisnorlax's <a target='_blank' href="https://chibisnorlax.github.io/acnhfaq/hhp/unlocks/">ACNH FAQ</a>.
              </p>
              <p>
                Happy designing,
              <br />
                <img className='mayor-icon' src="src\assets\icons\kris-icon.png" alt="Kris icon"/> <em>Kris</em> of <em>Orion Island</em>
              </p>
            </div>
          </div>}

          <button className="checklist-button" onClick={() => setRemaining(!remaining)}>
            Get Remaining Items
          </button>
          {remaining && <div className="overlay-background">
            <div className="overlay">
              <h3>Coming soon!</h3>
            </div>
          </div>}
        </div>
      </div>
    </div>
  )
}

export default Sidebar
