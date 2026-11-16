import { Link } from 'react-router-dom'

export default function HomePage() {
  return (
    <>
      <h1>Portfolio</h1>
      <p className="lead">Placeholder introduction.</p>
      <p>
        <Link to="/experiences">View all experiences</Link>
      </p>
    </>
  )
}
