import { NavLink, Outlet } from 'react-router-dom'

export default function Layout() {
  return (
    <>
      <header className="site-header">
        <nav aria-label="Main">
          <ul className="site-nav__list">
            <li>
              <NavLink to="/" end className="site-nav__link">
                Home
              </NavLink>
            </li>
            <li>
              <NavLink to="/experiences" className="site-nav__link">
                Experiences
              </NavLink>
            </li>
          </ul>
        </nav>
      </header>
      <main className="site-main">
        <Outlet />
      </main>
    </>
  )
}
