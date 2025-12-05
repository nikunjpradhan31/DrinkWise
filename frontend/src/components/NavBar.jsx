import { useContext, useState } from 'react';
import { Film, Menu, X, User, LogOut, ChevronDown } from 'lucide-react';
import { AuthContext } from '../context/AuthContext';
import Image from '../assets/himalayanhutwhite.png'

export default function NavbarComponent() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  
  const auth = useContext(AuthContext)

  if (!auth) {
    throw new Error('AuthContext must be used within an AuthContextProvider');
  }

  const { user, logoutUser } = auth;

  const navigation = [
    { name: 'Movies', href: '/', current: false },
    { name: 'Watchlists', href: '/watchlist', current: false },
    { name: 'Friends', href: '/friends', current: false },
  ];

  return (
    <div className="fixed top-0 left-0 right-0 z-50">
      {/* Background blur overlay */}
      <div className="absolute inset-0 bg-black/20 backdrop-blur-xl border-b border-white/10"></div>
      
      {/* Navbar content */}
      <nav className="relative z-10 px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand - your exact text */}
          <div className="flex items-center">
            <a href="/movie" className="flex items-center gap-3 text-white hover:text-purple-300 transition-colors duration-200">
              <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-purple-700 rounded-lg flex items-center justify-center shadow-lg shadow-purple-500/25">
                      <img src={Image} alt="Himalayan Hut White" />

              </div>
              <span className="text-xl font-bold tracking-tight">Himalayan Hut</span>
            </a>
          </div>

          {/* Desktop Navigation - your exact navigation array */}
          <div className="hidden md:block">
            <div className="flex items-center space-x-1">
              {navigation.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    item.current
                      ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                      : 'text-gray-300 hover:text-white hover:bg-white/10'
                  }`}
                >
                  {item.name}
                </a>
              ))}
            </div>
          </div>

          {/* User Menu - your exact dropdown logic */}
          <div className="hidden md:block">
            <div className="relative">
              <button
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white hover:bg-white/10 transition-all duration-200 backdrop-blur-sm"
              >
                <User className="w-4 h-4" />
                <span className="text-sm font-medium">{user?.username || 'Guest'}</span>
                <ChevronDown className={`w-4 h-4 transition-transform duration-200 ${isDropdownOpen ? 'rotate-180' : ''}`} />
              </button>
              
              {/* Dropdown Menu - your exact items */}
              {isDropdownOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-black/80 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl overflow-hidden">
                  <div className="py-1">
                    <a
                      href={`/profile/${user.user_id}`}
                      className="flex items-center gap-3 px-4 py-3 text-sm text-gray-300 hover:text-white hover:bg-white/10 transition-colors duration-200"
                    >
                      <User className="w-4 h-4" />
                      Your Profile
                    </a>
                    <button
                      onClick={logoutUser}
                      className="w-full flex items-center gap-3 px-4 py-3 text-sm text-gray-300 hover:text-white hover:bg-white/10 transition-colors duration-200 text-left"
                    >
                      <LogOut className="w-4 h-4" />
                      Sign Out
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="p-2 text-white hover:text-purple-300 hover:bg-white/10 rounded-lg transition-all duration-200"
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu - your exact navigation items */}
        {isMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 bg-black/40 backdrop-blur-xl border border-white/10 rounded-xl mt-2 shadow-2xl">
              {navigation.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  className={`block px-3 py-2 rounded-lg text-base font-medium transition-all duration-200 ${
                    item.current
                      ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                      : 'text-gray-300 hover:text-white hover:bg-white/10'
                  }`}
                  onClick={() => setIsMenuOpen(false)}
                >
                  {item.name}
                </a>
              ))}
              
              {/* Mobile User Menu */}
              <div className="border-t border-white/10 pt-3 mt-3">
                <a
                  href={`/profile/${user.user_id}`}
                  className="flex items-center gap-3 px-3 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors duration-200"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <User className="w-4 h-4" />
                  Your Profile
                </a>
                <button
                  onClick={() => {
                    logoutUser();
                    setIsMenuOpen(false);
                  }}
                  className="w-full flex items-center gap-3 px-3 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors duration-200 text-left"
                >
                  <LogOut className="w-4 h-4" />
                  Sign Out
                </button>
              </div>
            </div>
          </div>
        )}
      </nav>
    </div>
  );
}