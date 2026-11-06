import { NavLink, Outlet } from 'react-router-dom'

export default function Layout() {
  return (
    <>
      <header>
        <nav aria-label="Main">
          <ul>
            <li>
              <NavLink to="/" end>
                Home
              </NavLink>
            </li>
            <li>
              <NavLink to="/experiences">Experiences</NavLink>
            </li>
          </ul>
        </nav>
      </header>
      <main>
        <Outlet />
      </main>
    </>
  )
}
