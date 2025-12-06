import { useContext, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { CupSoda, Menu, X, User, LogOut, ChevronDown } from "lucide-react";
import { AuthContext } from "../context/AuthContext";

export default function NavbarComponent() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const location = useLocation();

  const auth = useContext(AuthContext);

  if (!auth) {
    throw new Error("AuthContext must be used within an AuthContextProvider");
  }

  const { user, logoutUser } = auth;

  const navigation = [
    { name: "Discover", href: "/" },
    { name: "Account", href: "/account" },
  ];

  const isActive = (href) =>
    href === "/"
      ? location.pathname === "/"
      : location.pathname.startsWith(href);

  return (
    <div className="fixed top-0 left-0 right-0 z-50">
      <div className="absolute inset-0 bg-slate-950/70 backdrop-blur-xl border-b border-blue-400/20"></div>

      <nav className="relative z-10 px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand */}
          <div className="flex items-center">
            <Link
              to="/"
              className="flex items-center gap-3 text-white hover:text-blue-200 transition-colors duration-200"
            >
              <div className="w-9 h-9 bg-gradient-to-r from-blue-500 to-blue-700 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/25">
                <CupSoda className="w-5 h-5" />
              </div>
              <span className="text-xl font-bold tracking-tight">DrinkWise</span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:block">
            <div className="flex items-center space-x-1">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive(item.href)
                      ? "bg-blue-500/20 text-blue-100 border border-blue-500/30"
                      : "text-gray-300 hover:text-white hover:bg-white/10"
                  }`}
                >
                  {item.name}
                </Link>
              ))}
            </div>
          </div>

          {/* User Menu */}
          <div className="hidden md:block">
            <div className="relative">
              <button
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white hover:bg-white/10 transition-all duration-200 backdrop-blur-sm"
              >
                <User className="w-4 h-4" />
                <span className="text-sm font-medium">
                  {user?.username || "Guest"}
                </span>
                <ChevronDown
                  className={`w-4 h-4 transition-transform duration-200 ${
                    isDropdownOpen ? "rotate-180" : ""
                  }`}
                />
              </button>

              {isDropdownOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-slate-950/90 backdrop-blur-xl border border-blue-400/20 rounded-xl shadow-2xl overflow-hidden">
                  <div className="py-1">
                    <Link
                      to="/account"
                      className="flex items-center gap-3 px-4 py-3 text-sm text-gray-300 hover:text-white hover:bg-blue-500/10 transition-colors duration-200"
                    >
                      <User className="w-4 h-4" />
                      Account
                    </Link>
                    <button
                      onClick={logoutUser}
                      className="w-full flex items-center gap-3 px-4 py-3 text-sm text-gray-300 hover:text-white hover:bg-blue-500/10 transition-colors duration-200 text-left"
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
              className="p-2 text-white hover:text-blue-200 hover:bg-white/10 rounded-lg transition-all duration-200"
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 bg-slate-950/90 backdrop-blur-xl border border-blue-400/20 rounded-xl mt-2 shadow-2xl">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`block px-3 py-2 rounded-lg text-base font-medium transition-all duration-200 ${
                    isActive(item.href)
                      ? "bg-blue-500/20 text-blue-100 border border-blue-500/30"
                      : "text-gray-300 hover:text-white hover:bg-white/10"
                  }`}
                  onClick={() => setIsMenuOpen(false)}
                >
                  {item.name}
                </Link>
              ))}

              <div className="border-t border-white/10 pt-3 mt-3">
                <Link
                  to="/account"
                  className="flex items-center gap-3 px-3 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors duration-200"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <User className="w-4 h-4" />
                  Account
                </Link>
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
