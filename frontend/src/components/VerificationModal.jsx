import React, { useState, useContext, useRef } from "react";
import { AuthContext } from "../context/AuthContext";
import { ArrowLeft, Shield, Check } from 'lucide-react';

const VerifyModal = (type) => {
    const authContext = useContext(AuthContext);
    
    if (!authContext) {
        throw new Error("AuthContext must be used within an AuthContextProvider");
    }
    
    const {
        VerifyLoginUser,
        showVerify,
        setshowVerify,
        verifyError,
        verifyInfo,
        setverifyInfo,
        setverifyError,
        user
    } = authContext;
    
    const [code, setCode] = useState("");
    
    const [digits, setDigits] = useState(['', '', '', '', '', '']);
    const inputRefs = useRef([]);

    const handleSubmit = async () => {
        const intCode = parseInt(code, 10);

        if (isNaN(intCode) || code.length !== 6) {
            setverifyError("Please enter a valid 6-digit code.");
            return;
        }

        const newVerifyInfo = {
            ...verifyInfo,
            code: intCode
        };

        setverifyInfo(newVerifyInfo);

        const result = await VerifyLoginUser(newVerifyInfo);

        if (result.success) {
            setverifyInfo({});
            setCode("");
            handleClose();
        }
    };
    
    const handleClose = () => {
        setCode("");
        setverifyError("");
        setshowVerify(false);
        setDigits(['', '', '', '', '', '']);
    };

    // Handle individual digit input
    const handleDigitChange = (index, value) => {
        if (value.length > 1) return; 
        if (!/^\d*$/.test(value)) return; 

        const newDigits = [...digits];
        newDigits[index] = value;
        setDigits(newDigits);
        
        const newCode = newDigits.join('');
        setCode(newCode);

        if (value && index < 5) {
            inputRefs.current[index + 1]?.focus();
        }
    };

    const handleKeyDown = (index, e) => {
        if (e.key === 'Backspace' && !digits[index] && index > 0) {
            inputRefs.current[index - 1]?.focus();
        }
    };

    const handlePaste = (e) => {
        e.preventDefault();
        const pasteData = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
        const newDigits = pasteData.split('').concat(Array(6).fill('')).slice(0, 6);
        setDigits(newDigits);
        setCode(pasteData);
        
        // Focus the next empty input or the last one
        const nextEmptyIndex = newDigits.findIndex(digit => !digit);
        const focusIndex = nextEmptyIndex === -1 ? 5 : nextEmptyIndex;
        inputRefs.current[focusIndex]?.focus();
    };

    if (!showVerify) return null;

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <div className="bg-black/80 backdrop-blur-xl border border-white/10 rounded-2xl p-8 w-full max-w-md shadow-2xl">
                {/* Header */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-purple-500 to-purple-700 rounded-2xl mb-4 shadow-lg shadow-purple-500/25">
                        <Shield className="w-8 h-8 text-white" />
                    </div>
                    <h2 className="text-2xl font-bold text-white mb-2">
                        Verify Your Account
                    </h2>
                    <p className="text-gray-400 text-sm">
                        Enter the 6-digit code sent to your device
                    </p>
                </div>

                <div className="mb-6">
                    <div className="flex justify-center gap-3 mb-6">
                        {digits.map((digit, index) => (
                            <div key={index} className="relative">
                                <input
                                    ref={el => inputRefs.current[index] = el}
                                    type="text"
                                    inputMode="numeric"
                                    maxLength={1}
                                    value={digit}
                                    onChange={(e) => handleDigitChange(index, e.target.value)}
                                    onKeyDown={(e) => handleKeyDown(index, e)}
                                    onPaste={handlePaste}
                                    className="w-12 h-14 bg-white/5 border-b-2 border-white/20 text-white text-xl font-bold text-center focus:outline-none focus:border-purple-500 transition-all duration-200 rounded-t-lg backdrop-blur-sm hover:bg-white/10"
                                    style={{ 
                                        caretColor: 'transparent',
                                        fontSize: '1.5rem'
                                    }}
                                />
                                {/* Underline indicator */}
                                <div className={`absolute bottom-0 left-0 right-0 h-0.5 transition-all duration-200 ${
                                    digit ? 'bg-purple-500' : 'bg-white/20'
                                }`}></div>
                            </div>
                        ))}
                    </div>
                </div>

                {verifyError && (
                    <div className="mb-6 p-3 bg-red-500/10 border border-red-500/20 rounded-xl backdrop-blur-sm">
                        <p className="text-red-400 text-sm text-center font-medium">{verifyError}</p>
                    </div>
                )}

                <div className="flex gap-3">
                    <button
                        onClick={handleClose}
                        className="flex items-center justify-center gap-2 px-4 py-3 bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white border border-white/10 rounded-xl transition-all duration-200 font-medium backdrop-blur-sm"
                    >
                        <ArrowLeft className="w-4 h-4" />
                        <span>Go Back</span>
                    </button>

                    <button
                        onClick={handleSubmit}
                        disabled={code.length !== 6}
                        className="flex-1 flex items-center justify-center gap-2 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white font-semibold py-3 px-4 rounded-xl transition-all duration-200 transform hover:scale-[1.02] focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-black disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none shadow-lg shadow-purple-500/25"
                    >
                        <Check className="w-4 h-4" />
                        <span>Submit</span>
                    </button>
                </div>

                {/* Helper Text */}
                {/* <div className="mt-6 text-center">
                    <p className="text-xs text-gray-500">
                        Didn't receive the code?{" "}
                        <button className="text-purple-400 hover:text-purple-300 font-medium transition-colors duration-200">
                            Resend
                        </button>
                    </p>
                </div> */}
            </div>
        </div>
    );
};

export default VerifyModal;